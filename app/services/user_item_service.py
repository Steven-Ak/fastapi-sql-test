from app.services.base_service import BaseService
from app.repositories.user_item_repository import UserItemRepository
from app.schemas.user_item_schema import UserItemCreate
from app.models.user_item_model import UserItem
from sqlalchemy.exc import IntegrityError
from app.core.exceptions import DuplicateException, NotFoundException

class UserItemService(BaseService[UserItem]):
    def __init__(self, repo: UserItemRepository):
        super().__init__(repo, UserItem)

    def assign_item_to_user(self, data: UserItemCreate):
        try:
            user_item = UserItem(**data.model_dump())
            return self.repo.create(user_item)
        except IntegrityError:
            raise DuplicateException("UserItem", "user_id and item_id combination")
    
    def get_user_items(self, user_id: int):
        return self.repo.get_items_by_user(user_id)
    
    def get_item_users(self, item_id: int):
        return self.repo.get_users_by_item(item_id)