from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import List

class EmbedRequest(BaseModel):
    text: str = Field(..., description="Text to embed")

class EmbedChunkResponse(BaseModel):
    id: UUID
    content: str
    chunk_index: int
    total_chunks: int
    embedding: List[float]
    created_at: datetime

    class Config:
        from_attributes = True

class EmbedResponse(BaseModel):
    chunks_stored: int
    processing_time_ms: float
    chunks: List[EmbedChunkResponse]