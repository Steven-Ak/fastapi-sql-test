from sqlalchemy.orm import Session
from app.repositories.base_repository import BaseRepository
from app.models.embedding_model import Embedding
from uuid import UUID

class EmbeddingRepository(BaseRepository[Embedding]):
    def __init__(self, db: Session):
        super().__init__(db, Embedding)

    def get_by_user_id(self, user_id: UUID):
        return self.db.query(Embedding).filter(Embedding.user_id == user_id).all()