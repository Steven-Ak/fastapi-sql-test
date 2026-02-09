from sqlalchemy.orm import Session
from app.repositories.base_repository import BaseRepository
from app.models.user_item_model import UserItem

class UserItemRepository(BaseRepository[UserItem]):
    def __init__(self, db: Session):
        super().__init__(db, UserItem)
    
    def get_items_by_user(self, user_id: int):
        return self.db.query(UserItem).filter(UserItem.user_id == user_id).all()
    
    def get_users_by_item(self, item_id: int):
        return self.db.query(UserItem).filter(UserItem.item_id == item_id).all()