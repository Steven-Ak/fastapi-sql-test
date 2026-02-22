from fastapi import Depends, Query
from sqlalchemy.orm import Session
from enum import Enum
from typing import Generator

from app.clients.database_clients import get_postgres_db, get_supabase_db
from app.repositories.chat_repository import ChatRepository
from app.repositories.item_repository import ItemRepository
from app.repositories.user_repository import UserRepository
from app.repositories.user_item_repository import UserItemRepository
from app.services.chat_service import ChatService
from app.services.item_service import ItemService
from app.services.user_service import UserService
from app.services.user_item_service import UserItemService


class DBSource(str, Enum):
    POSTGRES = "postgres"
    SUPABASE = "supabase"


def get_db_session(
    db_source: DBSource = Query(DBSource.POSTGRES, description="Database source")
) -> Generator[Session, None, None]:
    if db_source == DBSource.POSTGRES:
        yield from get_postgres_db()
    else:
        yield from get_supabase_db()


# ===== Service dependencies (all use the single session) =====
def get_item_service(db: Session = Depends(get_db_session)) -> ItemService:
    return ItemService(ItemRepository(db))


def get_user_service(db: Session = Depends(get_db_session)) -> UserService:
    return UserService(UserRepository(db))


def get_user_item_service(db: Session = Depends(get_db_session)) -> UserItemService:
    return UserItemService(UserItemRepository(db))


def get_chat_service(db: Session = Depends(get_db_session)) -> ChatService:
    return ChatService(ChatRepository(db))