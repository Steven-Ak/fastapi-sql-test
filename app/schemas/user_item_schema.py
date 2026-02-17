from uuid import UUID
from pydantic import BaseModel

class UserItemCreate(BaseModel):
    user_id: UUID
    item_id: UUID

class UserItemResponse(UserItemCreate):
    id: UUID

    class Config:
        from_attributes = True