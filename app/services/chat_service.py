import time
from typing import List, Optional
from datetime import datetime, timezone
from uuid import UUID
from app.schemas.chat_schema import ChatRequest, ChatResponse, ImageDescribeResponse, LLMProvider
from app.models.chat_model import Chat, ChatMessageRecord
from app.repositories.chat_repository import ChatRepository
from app.clients.llm_clients.llm_manager import get_cohere_client
from app.clients.storage_clients.storage_base_client import BaseStorageClient
from app.services.summarization_service import SummarizationService
from app.utils.context_builder import build_optimized_context
from app.utils.token_parser import extract_token_usage, extract_billed_units
from app.core.exceptions import NotFoundException, ForbiddenException


class ChatService:
    """Service for handling LLM chat requests with persistent history."""

    def __init__(
        self,
        chat_repo: ChatRepository,
        summarization_service: SummarizationService,
        storage: BaseStorageClient,
    ):
        self.chat_repo = chat_repo
        self.summarization_service = summarization_service
        self.storage = storage

    # ----- Core chat -----

    def chat(
        self,
        request: ChatRequest,
        user_id: UUID,
        chat_id: Optional[UUID] = None,
    ) -> ChatResponse:
        """Send a chat request to the LLM with optimized conversation context."""

        # Resolve or create chat session
        if chat_id:
            chat = self._get_owned_chat(chat_id, user_id)
        else:
            title = self.summarization_service.generate_chat_title(
                request.messages, request.provider
            )
            chat = self.chat_repo.create_chat(Chat(user_id=user_id, title=title))

        # Persist new user messages
        for msg in request.messages:
            self.chat_repo.add_message(ChatMessageRecord(
                chat_id=chat.id,
                role=msg.role.value,
                content=msg.content,
            ))

        # Update message count before summarization check
        self.chat_repo.db.refresh(chat)
        chat.message_count = len(chat.messages)
        self.chat_repo.update_chat(chat)

        # Summarize if needed
        if self.summarization_service.should_generate_summary(chat):
            self.summarization_service.generate_summary(chat, request.provider, self.chat_repo)
            self.chat_repo.db.refresh(chat)

        # Build context and call LLM
        all_messages = build_optimized_context(chat)

        if request.provider == LLMProvider.COHERE:
            client = get_cohere_client()
            model = request.model or client.model
        else:
            raise NotFoundException(f"Provider {request.provider} not available")

        start_time = time.time()
        result = client.chat(
            messages=all_messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )
        response_time_ms = (time.time() - start_time) * 1000

        assistant_text = result["text"]
        self.chat_repo.add_message(ChatMessageRecord(
            chat_id=chat.id, role="assistant", content=assistant_text,
        ))
        chat.message_count = len(chat.messages) + 1
        chat.updated_at = datetime.now(timezone.utc)
        self.chat_repo.update_chat(chat)

        return ChatResponse(
            chat_id=chat.id,
            response=assistant_text,
            provider=request.provider,
            model=model,
            token_usage=extract_token_usage(result),
            response_time_ms=round(response_time_ms, 2),
            generation_id=result.get("generation_id"),
            billed_units=extract_billed_units(result),
            finish_reason=result.get("finish_reason"),
            meta=result.get("meta"),
            request_params={
                "temperature": request.temperature,
                "max_tokens": request.max_tokens,
                "messages_count": len(all_messages),
                "total_history_messages": len(chat.messages),
                "using_summary": chat.summary is not None,
            },
        )

    def describe_image(
        self,
        image_bytes: bytes,
        mime_type: str,
        prompt: str,
        user_id: UUID,
        file_id,
        filename: str,
    ) -> ImageDescribeResponse:
        """Describe an image using the vision model and upload it to storage."""
        import uuid as _uuid
        client = get_cohere_client()
        result = client.answer_image(
            image_bytes=image_bytes,
            mime_type=mime_type,
            prompt=prompt,
        )
        file_url = self.storage.upload_image_and_get_signed_url(
            user_id, file_id, image_bytes, filename
        )
        return ImageDescribeResponse(
            description=result["text"],
            file_url=file_url,
        )
    

    # ----- Chat session management -----

    def get_user_chats(self, user_id: UUID) -> List[Chat]:
        """List all chat sessions for a user."""
        return self.chat_repo.get_chats_by_user(user_id)

    def get_chat_history(self, chat_id: UUID, user_id: UUID) -> Chat:
        """Get full chat history (with ownership check)."""
        return self._get_owned_chat(chat_id, user_id)

    def delete_chat(self, chat_id: UUID, user_id: UUID) -> None:
        """Delete a chat session (with ownership check)."""
        chat = self._get_owned_chat(chat_id, user_id)
        self.chat_repo.delete_chat(chat)

    # ----- Private helpers -----

    def _get_owned_chat(self, chat_id: UUID, user_id: UUID) -> Chat:
        """Fetch a chat and verify ownership."""
        chat = self.chat_repo.get_chat_by_id(chat_id)
        if not chat:
            raise NotFoundException("Chat")
        if chat.user_id != user_id:
            raise ForbiddenException("You do not have access to this chat")
        return chat