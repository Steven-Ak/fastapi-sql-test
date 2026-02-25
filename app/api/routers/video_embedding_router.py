from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from app.schemas.base_schema import PaginatedResponse
from app.schemas.video_embedding_schema import VideoEmbedChunkResponse, VideoEmbedRequest, VideoEmbedResponse, VideoSummaryResponse
from app.services.video_embedding_service import VideoEmbeddingService
from app.models.user_model import User
from app.auth.auth_deps import get_current_user
from app.core.service_deps import get_video_embedding_service

router = APIRouter(prefix="/video-embed", tags=["Video Embeddings"])

@router.post("/", response_model=VideoEmbedResponse)
def embed_video(
    request: VideoEmbedRequest,
    current_user: User = Depends(get_current_user),
    service: VideoEmbeddingService = Depends(get_video_embedding_service),
):
    """Embed a YouTube video transcript and store it in the vector database"""
    try:
        records, processing_time_ms = service.embed_and_store(request.video_url, current_user.id)
        first = records[0]
        return VideoEmbedResponse(
            title=first.title,
            duration=first.duration,
            topics=first.topics,
            chunks_stored=len(records),
            processing_time_ms=round(processing_time_ms, 2),
            chunks=records,
        )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/", response_model=PaginatedResponse[VideoSummaryResponse])
def get_all_videos(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    service: VideoEmbeddingService = Depends(get_video_embedding_service),
):
    """Get all videos across all users (paginated)"""
    try:
        return service.get_all_paginated(page=page, page_size=page_size)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/me", response_model=PaginatedResponse[VideoSummaryResponse])
def get_my_videos(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    service: VideoEmbeddingService = Depends(get_video_embedding_service),
):
    """Get current user's videos (paginated)"""
    try:
        return service.get_user_videos_paginated(user_id=current_user.id, page=page, page_size=page_size)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/video/{video_id}", response_model=List[VideoEmbedChunkResponse])
def get_video_chunks(
    video_id: UUID,
    current_user: User = Depends(get_current_user),
    service: VideoEmbeddingService = Depends(get_video_embedding_service),
):
    """Get all chunks for a specific video"""
    try:
        return service.get_by_video_id(video_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chunk/{chunk_id}", response_model=VideoEmbedChunkResponse)
def get_chunk(
    chunk_id: UUID,
    current_user: User = Depends(get_current_user),
    service: VideoEmbeddingService = Depends(get_video_embedding_service),
):
    """Get a single chunk by its ID"""
    try:
        return service.get_by_chunk_id(chunk_id)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=500, detail=str(e))