from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime, timezone
from app.clients.database_clients import Base


class Chat(Base):
    __tablename__ = "chats"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    # Summarization fields
    summary = Column(Text, nullable=True)
    summary_up_to_message_id = Column(Integer, nullable=True)
    message_count = Column(Integer, default=0)

    user = relationship("User", back_populates="chats")
    messages = relationship("ChatMessageRecord", back_populates="chat", cascade="all, delete-orphan", order_by="ChatMessageRecord.created_at")


class ChatMessageRecord(Base):
    """Individual message within a chat session.
    Named ChatMessageRecord to avoid collision with the Pydantic ChatMessage schema.
    """
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(UUID(as_uuid=True), ForeignKey("chats.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String, nullable=False)  # "user", "assistant", "system"
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))

    chat = relationship("Chat", back_populates="messages")
