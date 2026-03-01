from fastapi import APIRouter, Depends, HTTPException, Query
from uuid import UUID
from typing import List
from app.schemas.video_embedding_schema import (
    VideoEmbedRequest,
    VideoEmbedResponse,
    VideoEmbedChunkResponse,
    VideoQuestionRequest,
    VideoQuestionResponse,
    VideoSummaryResponse,
    UserVideoResponse,
)
from app.schemas.base_schema import PaginatedResponse
from app.services.video_embedding_service import VideoEmbeddingService
from app.models.user_model import User
from app.auth.auth_deps import get_current_user
from app.core.service_deps import get_video_embedding_service
from app.core.exceptions import DuplicateException

router = APIRouter(prefix="/video-embed", tags=["Video Embeddings"])


@router.post("/", response_model=VideoEmbedResponse)
def embed_video(
    request: VideoEmbedRequest,
    current_user: User = Depends(get_current_user),
    service: VideoEmbeddingService = Depends(get_video_embedding_service),
):
    """Embed a YouTube video transcript and store it in the vector database"""
    try:
        video, chunks, processing_time_ms = service.embed_and_store(request.video_url, current_user.id)
        return VideoEmbedResponse(
            id=video.id,
            title=video.title,
            duration=video.duration,
            topics=video.topics,
            chunks_stored=len(chunks),
            processing_time_ms=round(processing_time_ms, 2),
            chunks=chunks,
        )
    except DuplicateException as e:
        raise HTTPException(status_code=409, detail=str(e))
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


@router.get("/my", response_model=PaginatedResponse[UserVideoResponse])
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


@router.get("/{video_id}/chunks", response_model=List[VideoEmbedChunkResponse])
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


@router.get("/chunks/{chunk_id}", response_model=VideoEmbedChunkResponse)
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


@router.post("/{video_id}/ask", response_model=VideoQuestionResponse)
def ask_video_question(
    video_id: UUID,
    request: VideoQuestionRequest,
    current_user: User = Depends(get_current_user),
    service: VideoEmbeddingService = Depends(get_video_embedding_service),
):
    """Ask a question about a video's content using RAG"""
    try:
        answer, source_chunks = service.answer_video_question(video_id, current_user.id, request.question)
        return VideoQuestionResponse(
            answer=answer,
            source_chunks=source_chunks
        )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=500, detail=str(e))