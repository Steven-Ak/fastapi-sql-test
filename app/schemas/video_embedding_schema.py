from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import List, Optional


class VideoEmbedRequest(BaseModel):
    video_url: str = Field(..., description="YouTube video URL")


class VideoEmbedChunkResponse(BaseModel):
    id: UUID
    video_id: UUID
    video_url: str
    title: str
    duration: int
    topics: Optional[List[str]] = None
    content: str
    chunk_index: int
    total_chunks: int
    start_time: float
    end_time: float
    created_at: datetime

    class Config:
        from_attributes = True


class VideoEmbedResponse(BaseModel):
    title: str
    duration: int
    topics: Optional[List[str]] = None
    chunks_stored: int
    processing_time_ms: float
    chunks: List[VideoEmbedChunkResponse]

class VideoSummaryResponse(BaseModel):
    video_id: UUID
    video_url: str
    title: str
    duration: int
    topics: Optional[List[str]] = None
    total_chunks: int
    created_at: datetime

    class Config:
        from_attributes = True