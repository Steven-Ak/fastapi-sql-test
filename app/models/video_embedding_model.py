from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
import uuid
from datetime import datetime, timezone
from app.clients.database_clients import Base
from app.core.config import settings


class Video(Base):
    __tablename__ = "videos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True, nullable=False)
    video_url = Column(String, nullable=False, unique=True)
    title = Column(String, nullable=False)
    duration = Column(Integer, nullable=False)
    topics = Column(ARRAY(String), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))

    chunks = relationship("VideoEmbeddingChunk", back_populates="video", cascade="all, delete-orphan")
    user_videos = relationship("UserVideo", back_populates="video", cascade="all, delete-orphan")


class UserVideo(Base):
    __tablename__ = "user_videos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id", ondelete="CASCADE"), nullable=False, index=True)
    added_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))

    user = relationship("User")
    video = relationship("Video", back_populates="user_videos")

    __table_args__ = (
        UniqueConstraint("user_id", "video_id", name="unique_user_video"),
    )


class VideoEmbeddingChunk(Base):
    __tablename__ = "video_embedding_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True, nullable=False)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id", ondelete="CASCADE"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(settings.EMBEDDING_DIMENSIONS), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    total_chunks = Column(Integer, nullable=False)
    start_time = Column(Float, nullable=False)
    end_time = Column(Float, nullable=False)

    video = relationship("Video", back_populates="chunks")