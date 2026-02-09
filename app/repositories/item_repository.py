from sqlalchemy.orm import Session
from app.repositories.base_repository import BaseRepository
from app.models.item_model import Item

class ItemRepository(BaseRepository[Item]):
    def __init__(self, db: Session):
        super().__init__(db, Item)
