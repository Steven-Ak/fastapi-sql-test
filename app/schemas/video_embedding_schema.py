from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import List, Optional


class VideoEmbedRequest(BaseModel):
    video_url: str = Field(..., description="YouTube video URL")


class VideoEmbedChunkResponse(BaseModel):
    id: UUID
    video_id: UUID
    content: str
    chunk_index: int
    total_chunks: int
    start_time: float
    end_time: float

    class Config:
        from_attributes = True


class VideoEmbedResponse(BaseModel):
    id: UUID
    title: str
    duration: int
    topics: Optional[List[str]] = None
    chunks_stored: int
    processing_time_ms: float
    chunks: List[VideoEmbedChunkResponse]


class VideoSummaryResponse(BaseModel):
    id: UUID
    video_url: str
    title: str
    duration: int
    topics: Optional[List[str]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class UserVideoResponse(BaseModel):
    id: UUID
    user_id: UUID
    video_id: UUID
    added_at: datetime
    video: VideoSummaryResponse

    class Config:
        from_attributes = True


class VideoQuestionRequest(BaseModel):
    question: str = Field(..., min_length=1, description="Question about the video content")


class VideoQuestionResponse(BaseModel):
    answer: str
    source_chunks: List[VideoEmbedChunkResponse]