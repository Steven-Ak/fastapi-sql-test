from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector
import uuid
from datetime import datetime, timezone
from app.clients.database_clients import Base
from app.core.config import settings


class VideoEmbedding(Base):
    __tablename__ = "video_embeddings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    video_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    video_url = Column(String, nullable=False)
    title = Column(String, nullable=False)
    duration = Column(Integer, nullable=False)  # in seconds
    topics = Column(ARRAY(String), nullable=True)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(settings.EMBEDDING_DIMENSIONS), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    total_chunks = Column(Integer, nullable=False)
    start_time = Column(Float, nullable=False)  # seconds from video start
    end_time = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))