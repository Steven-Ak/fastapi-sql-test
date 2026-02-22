import uuid
from sqlalchemy import UUID, Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.clients.database_clients import Base

class UserItem(Base):
    __tablename__ = "user_items"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    item_id = Column(UUID(as_uuid=True), ForeignKey("items.id"), nullable=False)

    user = relationship("User", back_populates="items")
    item = relationship("Item", back_populates="user_items")

    __table_args__ = (
        UniqueConstraint('user_id', 'item_id', name='unique_user_item'),
    )