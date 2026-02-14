from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session

from app.schemas.chat_schema import (
    ChatRequest, 
    ChatResponse, 
    ChatSessionResponse, 
    ChatHistoryResponse,
    LLMProvider,
)
from app.services.chat_service import ChatService
from app.repositories.chat_repository import ChatRepository
from app.models.user_model import User
from app.api.auth_deps import get_current_user
from app.clients.database_clients import get_db

router = APIRouter(prefix="/chat", tags=["Chat"])


def get_chat_service(db: Session = Depends(get_db)) -> ChatService:
    return ChatService(ChatRepository(db))


@router.post("/", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service),
    chat_id: Optional[int] = Query(default=None, description="Pass a chat_id to continue an existing conversation. Omit to start a new chat."),
):
    """
    Chat with the LLM.
    
    - Omit `chat_id` → a new conversation is created automatically.
    - Pass `chat_id` → the model receives all prior messages as context.
    
    """
    try:
        return service.chat(request, user_id=current_user.id, chat_id=chat_id)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions", response_model=List[ChatSessionResponse])
def list_chats(
    current_user: User = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service),
):
    """List all chat sessions for the current user"""
    return service.get_user_chats(current_user.id)


@router.get("/sessions/{chat_id}", response_model=ChatHistoryResponse)
def get_chat_history(
    chat_id: int,
    current_user: User = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service),
):
    """Get full message history for a chat session"""
    return service.get_chat_history(chat_id, current_user.id)


@router.delete("/sessions/{chat_id}", status_code=204)
def delete_chat(
    chat_id: int,
    current_user: User = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service),
):
    """Delete a chat session and all its messages"""
    service.delete_chat(chat_id, current_user.id)


@router.get("/models/{provider}")
def get_available_models(provider: LLMProvider):
    """
    Get available models for a provider
    """
    try:
        if provider == LLMProvider.COHERE:
            from app.clients.llm_clients.llm_manager import get_cohere_client
            client = get_cohere_client()
            return {
                "provider": provider,
                "models": client.available_models
            }
        else:
            raise HTTPException(
                status_code=404, 
                detail=f"Provider {provider} not configured"
            )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))