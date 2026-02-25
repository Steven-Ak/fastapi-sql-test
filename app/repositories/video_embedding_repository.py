from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.repositories.base_repository import BaseRepository
from app.models.video_embedding_model import Video, VideoEmbeddingChunk, UserVideo
from uuid import UUID
from typing import Tuple, List


class VideoRepository(BaseRepository[Video]):
    def __init__(self, db: Session):
        super().__init__(db, Video)

    def get_by_video_id_str(self, video_id_str: str):
        """Look up a global Video record by YouTube video ID substring in the URL."""
        return self.db.query(Video).filter(
            Video.video_url.contains(video_id_str)
        ).first()

    def get_all_paginated(self, skip: int, limit: int) -> Tuple[List[Video], int]:
        query = self.db.query(Video)
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total


class UserVideoRepository(BaseRepository[UserVideo]):
    def __init__(self, db: Session):
        super().__init__(db, UserVideo)

    def get_by_user_id(self, user_id: UUID) -> List[UserVideo]:
        return self.db.query(UserVideo).filter(UserVideo.user_id == user_id).all()

    def get_by_user_id_paginated(self, user_id: UUID, skip: int, limit: int) -> Tuple[List[UserVideo], int]:
        query = self.db.query(UserVideo).filter(UserVideo.user_id == user_id)
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total

    def get_by_user_and_video(self, user_id: UUID, video_id: UUID):
        return self.db.query(UserVideo).filter(
            UserVideo.user_id == user_id,
            UserVideo.video_id == video_id,
        ).first()


class VideoChunkRepository(BaseRepository[VideoEmbeddingChunk]):
    def __init__(self, db: Session):
        super().__init__(db, VideoEmbeddingChunk)

    def get_by_video_id(self, video_id: UUID) -> List[VideoEmbeddingChunk]:
        return self.db.query(VideoEmbeddingChunk).filter(
            VideoEmbeddingChunk.video_id == video_id
        ).all()

    def get_by_chunk_id(self, chunk_id: UUID):
        return self.db.query(VideoEmbeddingChunk).filter(
            VideoEmbeddingChunk.id == chunk_id
        ).first()

    def search_similar_chunks(self, video_id: UUID, query_embedding: List[float], limit: int = 5):
        """Search for chunks within a specific video that are similar to the query embedding."""
        return self.db.query(VideoEmbeddingChunk).filter(
            VideoEmbeddingChunk.video_id == video_id
        ).order_by(
            VideoEmbeddingChunk.embedding.cosine_distance(query_embedding)
        ).limit(limit).all()