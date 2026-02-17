import uuid
from sqlalchemy import UUID, Column, Integer, String
from app.clients.database_clients import Base
from sqlalchemy.orm import relationship

class Item(Base):
    __tablename__ = "items"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)

    user_items = relationship("UserItem", back_populates="item", cascade="all, delete-orphan")