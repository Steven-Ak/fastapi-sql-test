from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    email: str
    full_name: str

class UserResponse(UserCreate):
    id: int

    class Config:
        from_attributes = True