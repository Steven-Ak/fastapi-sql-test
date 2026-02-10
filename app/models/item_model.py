from sqlalchemy import Column, Integer, String
from app.clients.database_clients import Base
from sqlalchemy.orm import relationship

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)

    user_items = relationship("UserItem", back_populates="item", cascade="all, delete-orphan")