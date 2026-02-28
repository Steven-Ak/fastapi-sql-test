from fastapi import Depends, Query
from sqlalchemy.orm import Session
from enum import Enum
from typing import Generator

from app.clients.database_clients import get_postgres_db, get_supabase_db
from app.clients.storage_clients.supabase_storage import SupabaseStorage
from app.clients.storage_clients.storage_base_client import BaseStorageClient
from app.clients.llm_clients.llm_manager import get_llm_client
from app.repositories.chat_repository import ChatRepository
from app.repositories.embedding_repository import EmbeddingRepository
from app.repositories.item_repository import ItemRepository
from app.repositories.user_repository import UserRepository
from app.repositories.user_item_repository import UserItemRepository
from app.services.chat_service import ChatService
from app.services.embedding_service import EmbeddingService
from app.services.item_service import ItemService
from app.services.user_service import UserService
from app.services.user_item_service import UserItemService
from app.services.summarization_service import SummarizationService
from app.repositories.video_embedding_repository import VideoChunkRepository, VideoRepository, UserVideoRepository
from app.services.video_embedding_service import VideoEmbeddingService
from app.repositories.cv_repository import CVRepository, CVDetailsRepository
from app.services.cv_service import CVService


class DBSource(str, Enum):
    POSTGRES = "postgres"
    SUPABASE = "supabase"


def get_db_session(
    db_source: DBSource = Query(DBSource.SUPABASE, description="Database source")
) -> Generator[Session, None, None]:
    if db_source == DBSource.SUPABASE:
        yield from get_supabase_db()
    else:
        yield from get_postgres_db()


def get_storage_client() -> BaseStorageClient:
    """Dependency: returns the configured storage client."""
    return SupabaseStorage()


# ===== Service dependencies (all use the single session) =====
def get_item_service(db: Session = Depends(get_db_session)) -> ItemService:
    return ItemService(ItemRepository(db))


def get_user_service(db: Session = Depends(get_db_session)) -> UserService:
    return UserService(UserRepository(db))


def get_user_item_service(db: Session = Depends(get_db_session)) -> UserItemService:
    return UserItemService(UserItemRepository(db))


def get_chat_service(
    db: Session = Depends(get_db_session),
    storage: BaseStorageClient = Depends(get_storage_client),
) -> ChatService:
    summarization_svc = SummarizationService(get_llm_client)
    return ChatService(
        chat_repo=ChatRepository(db),
        summarization_service=summarization_svc,
        storage=storage,
    )


def get_embedding_service(db: Session = Depends(get_db_session)) -> EmbeddingService:
    return EmbeddingService(EmbeddingRepository(db))


def get_video_embedding_service(db: Session = Depends(get_db_session)) -> VideoEmbeddingService:
    return VideoEmbeddingService(
        video_repo=VideoRepository(db),
        chunk_repo=VideoChunkRepository(db),
        user_video_repo=UserVideoRepository(db),
    )


def get_cv_service(
    db: Session = Depends(get_db_session),
    storage: BaseStorageClient = Depends(get_storage_client),
) -> CVService:
    return CVService(
        cv_repo=CVRepository(db),
        cv_details_repo=CVDetailsRepository(db),
        storage=storage,
    )