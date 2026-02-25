from typing import Tuple, List
from sqlalchemy.orm import Session
from app.repositories.base_repository import BaseRepository
from app.models.video_embedding_model import VideoEmbedding
from uuid import UUID


class VideoEmbeddingRepository(BaseRepository[VideoEmbedding]):
    def __init__(self, db: Session):
        super().__init__(db, VideoEmbedding)

    def get_by_user_and_url(self, user_id: UUID, video_url: str):
        return self.db.query(VideoEmbedding).filter(
            VideoEmbedding.user_id == user_id,
            VideoEmbedding.video_url == video_url,
        ).first()

    def get_by_user_id(self, user_id: UUID):
        return self.db.query(VideoEmbedding).filter(
            VideoEmbedding.user_id == user_id,
        ).all()

    def get_by_video_id(self, video_id: UUID):
        return self.db.query(VideoEmbedding).filter(
            VideoEmbedding.video_id == video_id,
        ).all()
    
    def get_all_videos_paginated(self, skip: int, limit: int):
        query = self.db.query(
            VideoEmbedding.video_id,
            VideoEmbedding.video_url,
            VideoEmbedding.title,
            VideoEmbedding.duration,
            VideoEmbedding.topics,
            VideoEmbedding.total_chunks,
            VideoEmbedding.created_at,
        ).distinct(VideoEmbedding.video_id)
    
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total

    def get_user_videos_paginated(self, user_id: UUID, skip: int, limit: int):
        query = self.db.query(
            VideoEmbedding.video_id,
            VideoEmbedding.video_url,
            VideoEmbedding.title,
            VideoEmbedding.duration,
            VideoEmbedding.topics,
            VideoEmbedding.total_chunks,
            VideoEmbedding.created_at,
        ).distinct(VideoEmbedding.video_id).filter(VideoEmbedding.user_id == user_id)
    
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total

    def get_by_video_id(self, video_id: UUID) -> List[VideoEmbedding]:
        return self.db.query(VideoEmbedding).filter(VideoEmbedding.video_id == video_id).all()

    def get_by_chunk_id(self, chunk_id: UUID) -> VideoEmbedding:
        return self.db.query(VideoEmbedding).filter(VideoEmbedding.id == chunk_id).first()