from pydantic import BaseModel
from typing import Optional

class ItemCreate(BaseModel):
    name: str
    description: Optional[str] = None

class ItemResponse(ItemCreate):
    id: int

    class Config:
        orm_mode = True