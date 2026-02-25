from fastapi import APIRouter, Depends, HTTPException
from app.schemas.embedding_schema import EmbedRequest, EmbedResponse
from app.services.embedding_service import EmbeddingService
from app.models.user_model import User
from app.auth.auth_deps import get_current_user
from app.core.service_deps import get_embedding_service

router = APIRouter(prefix="/embed", tags=["Embeddings"])

@router.post("/", response_model=EmbedResponse)
def embed_text(
    request: EmbedRequest,
    current_user: User = Depends(get_current_user),
    service: EmbeddingService = Depends(get_embedding_service),
):
    """Embed text and store it in the vector database"""
    try:
        records, processing_time_ms = service.embed_and_store(request.text, current_user.id)
        return EmbedResponse(
            chunks_stored=len(records),
            processing_time_ms=round(processing_time_ms, 2),
            chunks=records,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))