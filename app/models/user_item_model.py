from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base

class UserItem(Base):
    __tablename__ = "user_items"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)

    user = relationship("User", back_populates="items")
    item = relationship("Item", back_populates="user_items")

    __table_args__ = (
        UniqueConstraint('user_id', 'item_id', name='unique_user_item'),
    )