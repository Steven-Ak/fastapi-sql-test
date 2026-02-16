import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from uuid import UUID
from app.schemas.chat_schema import (
    ChatRequest, 
    ChatResponse, 
    LLMProvider, 
    TokenUsage,
    BilletedUnits,
    ChatSessionResponse,
    ChatHistoryResponse,
)
from app.models.chat_model import Chat, ChatMessageRecord
from app.repositories.chat_repository import ChatRepository
from app.clients.llm_clients.llm_manager import get_cohere_client, get_summarization_client
from app.core.exceptions import NotFoundException, ForbiddenException
from app.core.config import settings


class ChatService:
    """Service for handling LLM chat requests with persistent history"""
    
    def __init__(self, chat_repo: ChatRepository):
        self.chat_repo = chat_repo
    
    def chat(self, request: ChatRequest, user_id: int, chat_id: Optional[UUID] = None) -> ChatResponse:
        """Send chat request to LLM with optimized conversation context"""
        
        # --- Resolve or create chat session ---
        if chat_id:
            chat = self._get_owned_chat(chat_id, user_id)
        else:
            # Auto-create a new chat, title from the first user message
            first_user_msg = next(
                (m.content for m in request.messages if m.role.value == "user"), 
                "New Chat"
            )
            title = first_user_msg[:80] + ("..." if len(first_user_msg) > 80 else "")
            chat = self.chat_repo.create_chat(Chat(
                user_id=user_id,
                title=title,
            ))
        
        # --- Check if summarization is needed ---
        # --- Persist new messages FIRST (so we can count them properly) ---
        for msg in request.messages:
            self.chat_repo.add_message(ChatMessageRecord(
                chat_id=chat.id,
                role=msg.role.value,
                content=msg.content,
            ))
        
        # --- Update message count BEFORE summarization check ---
        self.chat_repo.db.refresh(chat)
        chat.message_count = len(chat.messages)
        self.chat_repo.update_chat(chat)
        
        # --- Check if summarization is needed ---
        should_summarize = self._should_generate_summary(chat)
        
        if should_summarize:
            self._generate_summary(chat, request.provider)
            self.chat_repo.db.refresh(chat)
        
        # --- Build optimized message list ---
        all_messages = self._build_optimized_context(chat)
        
        # --- Select LLM client ---
        if request.provider == LLMProvider.COHERE:
            client = get_cohere_client()
            model = request.model or client.model
        else:
            raise NotFoundException(f"Provider {request.provider} not available")
        
        # --- Call LLM ---
        start_time = time.time()
        
        result = client.chat(
            messages=all_messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        response_time_ms = (time.time() - start_time) * 1000
        
        # --- Persist new messages + assistant response ---
        
        assistant_text = result["text"]
        self.chat_repo.add_message(ChatMessageRecord(
            chat_id=chat.id,
            role="assistant",
            content=assistant_text,
        ))
        
        # Update message count
        chat.message_count = len(chat.messages) + 1
        chat.updated_at = datetime.now(timezone.utc)
        self.chat_repo.update_chat(chat)
        
        # --- Build response ---
        token_usage = self._extract_token_usage(result)
        
        return ChatResponse(
            chat_id=chat.id,
            response=assistant_text,
            provider=request.provider,
            model=model,
            token_usage=token_usage,
            response_time_ms=round(response_time_ms, 2),
            generation_id=result.get("generation_id"),
            billed_units=self._extract_billed_units(result),
            finish_reason=result.get("finish_reason"),
            meta=result.get("meta"),
            request_params={
                "temperature": request.temperature,
                "max_tokens": request.max_tokens,
                "messages_count": len(all_messages),
                "total_history_messages": len(chat.messages),
                "using_summary": chat.summary is not None,
            }
        )
    
    # -----  Context optimization methods -----

    def _should_generate_summary(self, chat: Chat) -> bool:
        """
        Determine if we should generate or update a summary.
        """
        # Case 1: No summary yet - generate initial summary
        if not chat.summary:
            min_total_for_first_summary = settings.KEEP_RECENT_MESSAGES + settings.MIN_MESSAGES_TO_SUMMARIZE
            
            if chat.message_count >= settings.SUMMARIZE_THRESHOLD and chat.message_count >= min_total_for_first_summary:
                print(f"Initial summary needed: {chat.message_count} messages >= threshold {settings.SUMMARIZE_THRESHOLD}")
                return True
        
        # Case 2: Have summary - check if we need to update it
        elif chat.summary_up_to_message_id:
            messages_since_summary = [
                msg for msg in chat.messages 
                if msg.id > chat.summary_up_to_message_id
            ]
            new_message_count = len(messages_since_summary)
            min_new_for_update = settings.KEEP_RECENT_MESSAGES + settings.MIN_MESSAGES_TO_SUMMARIZE
            
            if new_message_count >= settings.SUMMARIZE_THRESHOLD and new_message_count >= min_new_for_update:
                print(f"🔄 Summary update needed: {new_message_count} new messages since last summary")
                return True
        
        return False
    
    def _build_optimized_context(self, chat: Chat) -> List[Dict[str, str]]:
        """
        Build optimized context using summary + recent messages
        Saves tokens by not sending all old messages
        """
        context = []
        
        # Add summary if available
        if chat.summary:
            context.append({
                "role": "system",
                "content": f"Previous conversation summary:\n{chat.summary}"
            })
            
            # Only include messages after the summary
            recent_messages = [
                msg for msg in chat.messages 
                if msg.id > (chat.summary_up_to_message_id or 0)
            ]
        else:
            # No summary yet, use all messages
            recent_messages = chat.messages
        
        # Keep only last N messages for token efficiency
        # This is a safety net in case we have way too many messages after summary
        if len(recent_messages) > settings.KEEP_RECENT_MESSAGES:
            recent_messages = recent_messages[-settings.KEEP_RECENT_MESSAGES:]
        
        for msg in recent_messages:
            context.append({
                "role": msg.role,
                "content": msg.content
            })
        
        return context
    
    def _generate_summary(self, chat: Chat, provider: LLMProvider):
        """
        Generate a summary of old messages to save tokens
        This is called automatically when message count exceeds threshold
        """
        # Determine which messages to summarize
        if chat.summary and chat.summary_up_to_message_id:
            # Update existing summary: summarize messages after last summary up to recent ones
            messages_after_summary = [
                msg for msg in chat.messages 
                if msg.id > chat.summary_up_to_message_id
            ]
            # Keep recent messages out of the summary
            messages_to_summarize = messages_after_summary[:-settings.KEEP_RECENT_MESSAGES]
        else:
            # Initial summary: summarize all except recent messages
            messages_to_summarize = chat.messages[:-settings.KEEP_RECENT_MESSAGES]
        
        if not messages_to_summarize or len(messages_to_summarize) < settings.MIN_MESSAGES_TO_SUMMARIZE:
            print(f"⚠️ Not enough messages to summarize: {len(messages_to_summarize)} < {settings.MIN_MESSAGES_TO_SUMMARIZE}")
            return
        
        # Build conversation text
        conversation_text = "\n".join([
            f"{msg.role.upper()}: {msg.content}"
            for msg in messages_to_summarize
        ])
        
        # Ask LLM to summarize
        if provider == LLMProvider.COHERE:
            client = get_summarization_client()
        else:
            return
        
        # Prepare summary prompt
        if chat.summary:
            # Updating existing summary
            summary_prompt = [{
                "role": "user",
                "content": f"""You are updating a conversation summary. Here is the previous summary:

{chat.summary}

Here are the new messages since that summary:

{conversation_text}

Write an updated summary from the assistant's perspective, incorporating both the previous context and new information. Use "I" and "we" language. Preserve all key facts, names, dates, and context. Keep it under 300 words.

Updated summary:"""
            }]
        else:
            # Creating initial summary
            summary_prompt = [{
                "role": "user",
                "content": f"""Summarize this conversation from the assistant's perspective. Write as if you (the assistant) are recalling what was discussed. Use "I" and "we" language. Preserve all key facts, names, dates, and context. Keep it under 200 words.

Conversation:
{conversation_text}

Write a first-person summary as the assistant:"""
            }]
        
        try:
            
            result = client.chat(
                messages=summary_prompt,
                temperature=0.3,  # Lower temperature for factual summary
                max_tokens=400
            )
            
            # Store summary
            chat.summary = result["text"]
            chat.summary_up_to_message_id = messages_to_summarize[-1].id
            self.chat_repo.update_chat(chat)
            
            print(f"✅ Generated summary for chat {chat.id} using {client.model} (summarized {len(messages_to_summarize)} messages up to ID {chat.summary_up_to_message_id})")
            
        except Exception as e:
            print(f"❌ Failed to generate summary for chat {chat.id}: {e}")
            # Continue without summary if it fails
    
    # ----- Chat session management -----
    
    def get_user_chats(self, user_id: int) -> List[Chat]:
        """List all chat sessions for a user"""
        return self.chat_repo.get_chats_by_user(user_id)
    
    def get_chat_history(self, chat_id: UUID, user_id: int) -> Chat:
        """Get full chat history (with ownership check)"""
        return self._get_owned_chat(chat_id, user_id)
    
    def delete_chat(self, chat_id: UUID, user_id: int) -> None:
        """Delete a chat session (with ownership check)"""
        chat = self._get_owned_chat(chat_id, user_id)
        self.chat_repo.delete_chat(chat)
    
    # ----- Private helpers -----
    
    def _get_owned_chat(self, chat_id: UUID, user_id: int) -> Chat:
        """Fetch a chat and verify ownership"""
        chat = self.chat_repo.get_chat_by_id(chat_id)
        if not chat:
            raise NotFoundException("Chat")
        if chat.user_id != user_id:
            raise ForbiddenException("You do not have access to this chat")
        return chat
    
    
    def _extract_token_usage(self, result: Dict[str, Any]) -> TokenUsage:
        """Extract token usage from Cohere response"""
        
        if "billed_units" in result and result["billed_units"]:
            billed = result["billed_units"]
            prompt_tokens = billed.get("input_tokens", 0) or 0
            completion_tokens = billed.get("output_tokens", 0) or 0
        elif "tokens" in result and result["tokens"]:
            tokens = result["tokens"]
            prompt_tokens = tokens.get("input_tokens", 0) or 0
            completion_tokens = tokens.get("output_tokens", 0) or 0
        else:
            prompt_tokens = 0
            completion_tokens = 0
        
        return TokenUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens
        )
    
    def _extract_billed_units(self, result: Dict[str, Any]) -> BilletedUnits | None:
        """Extract Cohere billing information"""
        
        if "billed_units" not in result or not result["billed_units"]:
            return None
        
        billed = result["billed_units"]
        return BilletedUnits(
            input_tokens=billed.get("input_tokens"),
            output_tokens=billed.get("output_tokens"),
            search_units=billed.get("search_units"),
            classifications=billed.get("classifications")
        )