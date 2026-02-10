from app.services.base_service import BaseService
from app.repositories.item_repository import ItemRepository
from app.schemas.item_schema import ItemCreate, ItemUpdate
from app.models.item_model import Item
from sqlalchemy.exc import IntegrityError
from app.core.exceptions import DuplicateException

class ItemService(BaseService[Item]):
    def __init__(self, repo: ItemRepository):
        super().__init__(repo, Item)

    def create_item(self, data: ItemCreate):
        try:
            item = Item(**data.model_dump())
            return self.repo.create(item)
        except IntegrityError:
            raise DuplicateException("Item", "name")

    def get_items(self):
        return self.get_all()
    
    def get_item(self, item_id: int):
        return self.get_by_id(item_id)

    def update_item(self, item_id: int, data: ItemCreate):
        item = self.get_by_id(item_id)
        item.name = data.name
        item.description = data.description
        try:
            return self.repo.update(item)
        except IntegrityError:
            raise DuplicateException("Item", "name")
    
    def patch_item(self, item_id: int, data: ItemUpdate):
        item = self.get_by_id(item_id)
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(item, key, value)
        try:
            return self.repo.update(item)
        except IntegrityError:
            raise DuplicateException("Item", "name")
    
    def delete_item(self, item_id: int):
        return self.delete(item_id)