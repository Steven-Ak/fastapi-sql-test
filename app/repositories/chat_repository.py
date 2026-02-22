from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from app.models.chat_model import Chat, ChatMessageRecord


class ChatRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_chat(self, chat: Chat) -> Chat:
        self.db.add(chat)
        self.db.commit()
        self.db.refresh(chat)
        return chat

    def get_chat_by_id(self, chat_id: UUID) -> Optional[Chat]:
        return (
            self.db.query(Chat)
            .options(joinedload(Chat.messages))
            .filter(Chat.id == chat_id)
            .first()
        )

    def get_chats_by_user(self, user_id: int) -> List[Chat]:
        return (
            self.db.query(Chat)
            .filter(Chat.user_id == user_id)
            .order_by(Chat.updated_at.desc())
            .all()
        )

    def add_message(self, message: ChatMessageRecord) -> ChatMessageRecord:
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message

    def update_chat(self, chat: Chat) -> Chat:
        self.db.commit()
        self.db.refresh(chat)
        return chat

    def delete_chat(self, chat: Chat) -> None:
        self.db.delete(chat)
        self.db.commit()
