from fastapi import Depends, Query
from sqlalchemy.orm import Session
from enum import Enum

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


# PostgreSQL dependencies
def get_item_service_postgres(db: Session = Depends(get_postgres_db)) -> ItemService:
    return ItemService(ItemRepository(db))


def get_user_service_postgres(db: Session = Depends(get_postgres_db)) -> UserService:
    return UserService(UserRepository(db))


def get_user_item_service_postgres(db: Session = Depends(get_postgres_db)) -> UserItemService:
    return UserItemService(UserItemRepository(db))


# Supabase dependencies
def get_item_service_supabase(db: Session = Depends(get_supabase_db)) -> ItemService:
    return ItemService(ItemRepository(db))


def get_user_service_supabase(db: Session = Depends(get_supabase_db)) -> UserService:
    return UserService(UserRepository(db))


def get_user_item_service_supabase(db: Session = Depends(get_supabase_db)) -> UserItemService:
    return UserItemService(UserItemRepository(db))

# ===== Dynamic database selection =====
def get_item_service(
    db_source: DBSource = Query(DBSource.POSTGRES, description="Database source"),
    postgres_db: Session = Depends(get_postgres_db),
    supabase_db: Session = Depends(get_supabase_db)
) -> ItemService:
    db = postgres_db if db_source == DBSource.POSTGRES else supabase_db
    return ItemService(ItemRepository(db))


def get_user_service(
    db_source: DBSource = Query(DBSource.POSTGRES, description="Database source"),
    postgres_db: Session = Depends(get_postgres_db),
    supabase_db: Session = Depends(get_supabase_db)
) -> UserService:
    db = postgres_db if db_source == DBSource.POSTGRES else supabase_db
    return UserService(UserRepository(db))


def get_user_item_service(
    db_source: DBSource = Query(DBSource.POSTGRES, description="Database source"),
    postgres_db: Session = Depends(get_postgres_db),
    supabase_db: Session = Depends(get_supabase_db)
) -> UserItemService:
    db = postgres_db if db_source == DBSource.POSTGRES else supabase_db
    return UserItemService(UserItemRepository(db))

def get_chat_service(
    db_source: DBSource = Query(DBSource.POSTGRES, description="Database source"),
    postgres_db: Session = Depends(get_postgres_db),
    supabase_db: Session = Depends(get_supabase_db)
) -> ChatService:
    db = postgres_db if db_source == DBSource.POSTGRES else supabase_db
    return ChatService(ChatRepository(db))