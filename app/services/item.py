from app.repositories.item import ItemRepository
from app.schemas.item import ItemCreate
from app.models.item import Item

class ItemService:
    def __init__(self, repo: ItemRepository):
        self.repo = repo

    def create_item(self, item_data: ItemCreate):
        item = Item(name=item_data.name, description=item_data.description)
        return self.repo.create(item)

    def get_items(self):
        return self.repo.get_all()

    def get_item(self, item_id: int):
        item = self.repo.get_by_id(item_id)
        if not item:
            raise ValueError("Item not found")
        return item

    def update_item(self, item_id: int, item_data: ItemCreate):
        item = self.repo.get_by_id(item_id)
        if not item:
            raise ValueError("Item not found")
        item.name = item_data.name
        item.description = item_data.description
        return self.repo.update(item)

    def delete_item(self, item_id: int):
        item = self.repo.get_by_id(item_id)
        if not item:
            raise ValueError("Item not found")
        self.repo.delete(item)
        return True