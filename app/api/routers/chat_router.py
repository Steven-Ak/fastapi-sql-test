from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
import json
import io
import pypdf
from app.clients.storage_clients.supabase_storage import SupabaseStorage
from fastapi import Form, File, UploadFile
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
from app.auth.auth_deps import get_current_user
from app.core.service_deps import get_chat_service

storage = SupabaseStorage()

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
):

    # Handle file extraction first so we can append to message
    if file and file.filename.lower().endswith('.pdf'):
        try:
            # Read file content
            contents = await file.read()
            
            # Extract text using pypdf
            pdf_file = io.BytesIO(contents)
            pdf_reader = pypdf.PdfReader(pdf_file)
            extracted_text = ""
            for page in pdf_reader.pages:
                extracted_text += page.extract_text() + "\n"
            
            # Append extracted text to message
            message = f"{message}\n\n[Attached PDF Content]:\n{extracted_text}"
            
            # Reset cursor for upload
            await file.seek(0)
            
        except Exception as e:
            print(f"Error extracting PDF text: {e}")
            # Continue without extraction, or could raise error
            pass

    # Build ChatRequest
    chat_request = ChatRequest(
            messages=[{"role":"user","content":message}],
            chat_id=chat_id,
            provider=provider,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )

    # Handle file
    try:
        response = service.chat(chat_request, user_id=current_user.id, chat_id=chat_request.chat_id)
        
        file_url = None
        if file:
            try:
                # If we haven't read contents yet
                if 'contents' not in locals():
                     contents = await file.read()
                
                # Use response.chat_id which is guaranteed to be set now
                file_url = storage.upload_pdf_and_get_signed_url(current_user.id, response.chat_id, contents, file.filename)
            except Exception as e:
                print(f"Supabase upload failed: {e}")
                # Don't fail the request if storage fails
                file_url = None

        response.file_url = file_url
        return response

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