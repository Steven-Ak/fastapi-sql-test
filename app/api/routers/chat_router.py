from typing import List, Optional
from uuid import UUID
import uuid
from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.core.service_deps import get_chat_service, get_storage_client
from app.utils.pdf_extractor import extract_text_from_pdf_bytes
from app.schemas.chat_schema import (
    ChatRequest,
    ChatResponse,
    ChatSessionResponse,
    ChatHistoryResponse,
    ImageDescribeResponse,
    LLMProvider,
)
from app.services.chat_service import ChatService
from app.models.user_model import User
from app.auth.auth_deps import get_current_user
from app.clients.storage_clients.storage_base_client import BaseStorageClient

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("/", response_model=ChatResponse)
async def chat(
    message: str = Form(..., description="The user message"),
    chat_id: Optional[UUID] | None = Form(None, description="Optional chat ID"),
    provider: str = Form("cohere", description="LLM provider"),
    model: str | None = Form(default="", description="Optional model selection"),
    temperature: float = Form(0.7, ge=0, le=1),
    max_tokens: int | None = Form(1000),
    file: UploadFile | None = File(None),
    current_user: User = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service),
    storage: BaseStorageClient = Depends(get_storage_client),
):
    # Extract text from attached PDF and append to the message
    contents = None
    if file and file.filename.lower().endswith(".pdf"):
        try:
            contents = await file.read()
            extracted_text = extract_text_from_pdf_bytes(contents)
            message = f"{message}\n\n[Attached PDF Content]:\n{extracted_text}"
            await file.seek(0)
        except Exception as e:
            print(f"Error reading PDF file: {e}")

    chat_request = ChatRequest(
        messages=[{"role": "user", "content": message}],
        chat_id=chat_id,
        provider=provider,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )

    try:
        response = service.chat(chat_request, user_id=current_user.id, chat_id=chat_request.chat_id)

        file_url = None
        if file:
            try:
                if contents is None:
                    contents = await file.read()
                file_url = storage.upload_pdf_and_get_signed_url(
                    current_user.id, response.chat_id, contents, file.filename
                )
            except Exception as e:
                print(f"Storage upload failed: {e}")

        response.file_url = file_url
        return response

    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/describe-image", response_model=ImageDescribeResponse)
async def answer_image(
    file: UploadFile = File(...),
    prompt: str = Form("Describe this image in detail."),
    current_user: User = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service),
):
    """Upload an image and get a description from Cohere's vision model."""
    ALLOWED = {"image/jpeg", "image/png", "image/gif", "image/webp"}
    if file.content_type not in ALLOWED:
        raise HTTPException(status_code=400, detail=f"Unsupported type: {file.content_type}")

    try:
        contents = await file.read()
        file_id = uuid.uuid4()
        return service.describe_image(
            image_bytes=contents,
            mime_type=file.content_type,
            prompt=prompt,
            user_id=current_user.id,
            file_id=file_id,
            filename=file.filename,
        )
    except Exception as e:
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
    chat_id: UUID,
    current_user: User = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service),
):
    """Get full message history for a chat session"""
    return service.get_chat_history(chat_id, current_user.id)


@router.delete("/sessions/{chat_id}", status_code=204)
def delete_chat(
    chat_id: UUID,
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