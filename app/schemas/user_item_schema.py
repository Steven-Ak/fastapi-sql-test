from pydantic import BaseModel

class UserItemCreate(BaseModel):
    user_id: int
    item_id: int

class UserItemResponse(UserItemCreate):
    id: int

    class Config:
        from_attributes = True