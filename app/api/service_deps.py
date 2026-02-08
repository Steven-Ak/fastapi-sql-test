from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.item_repository import ItemRepository
from app.repositories.user_repository import UserRepository
from app.repositories.user_item_repository import UserItemRepository
from app.services.item_service import ItemService
from app.services.user_service import UserService
from app.services.user_item_service import UserItemService

def get_item_service(db: Session = Depends(get_db)) -> ItemService:
    return ItemService(ItemRepository(db))

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(UserRepository(db))

def get_user_item_service(db: Session = Depends(get_db)) -> UserItemService:
    return UserItemService(UserItemRepository(db))