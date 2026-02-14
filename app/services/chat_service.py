import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
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
from app.clients.llm_clients.llm_manager import get_cohere_client
from app.core.exceptions import NotFoundException, ForbiddenException


class ChatService:
    """Service for handling LLM chat requests with persistent history"""
    
    def __init__(self, chat_repo: ChatRepository):
        self.chat_repo = chat_repo
    
    def chat(self, request: ChatRequest, user_id: int, chat_id: Optional[int] = None) -> ChatResponse:
        """Send chat request to LLM with full conversation context"""
        
        # --- Resolve or create chat session ---
        if chat_id:
            chat = self._get_owned_chat(chat_id, user_id)
        else:
            # Auto-create a new chat, title from the first user message
            first_user_msg = next(
                (m.content for m in request.messages if m.role.value == "user"), 
                "New Chat"
            )
            chat = self.chat_repo.create_chat(Chat(
                user_id=user_id,
                title=first_user_msg[:80],
            ))
        
        # --- Build the full message list: history + new messages ---
        history_messages = self._load_history_messages(chat)
        
        new_messages = [
            {"role": msg.role.value, "content": msg.content} 
            for msg in request.messages
        ]
        
        all_messages = history_messages + new_messages
        
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
        for msg in request.messages:
            self.chat_repo.add_message(ChatMessageRecord(
                chat_id=chat.id,
                role=msg.role.value,
                content=msg.content,
            ))
        
        assistant_text = result["text"]
        self.chat_repo.add_message(ChatMessageRecord(
            chat_id=chat.id,
            role="assistant",
            content=assistant_text,
        ))
        
        # Update chat timestamp
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
                "history_messages_count": len(history_messages),
            }
        )
    
    # ----- Chat session management -----
    
    def get_user_chats(self, user_id: int) -> List[Chat]:
        """List all chat sessions for a user"""
        return self.chat_repo.get_chats_by_user(user_id)
    
    def get_chat_history(self, chat_id: int, user_id: int) -> Chat:
        """Get full chat history (with ownership check)"""
        return self._get_owned_chat(chat_id, user_id)
    
    def delete_chat(self, chat_id: int, user_id: int) -> None:
        """Delete a chat session (with ownership check)"""
        chat = self._get_owned_chat(chat_id, user_id)
        self.chat_repo.delete_chat(chat)
    
    # ----- Private helpers -----
    
    def _get_owned_chat(self, chat_id: int, user_id: int) -> Chat:
        """Fetch a chat and verify ownership"""
        chat = self.chat_repo.get_chat_by_id(chat_id)
        if not chat:
            raise NotFoundException("Chat")
        if chat.user_id != user_id:
            raise ForbiddenException("You do not have access to this chat")
        return chat
    
    def _load_history_messages(self, chat: Chat) -> List[Dict[str, str]]:
        """Load prior messages from a chat session as dicts for the LLM client"""
        return [
            {"role": msg.role, "content": msg.content}
            for msg in chat.messages
        ]
    
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