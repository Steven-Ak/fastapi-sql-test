from pydantic import BaseModel, EmailStr
from typing import Optional, List

# Input model for creating/updating a user
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None

# Output model for API responses
class UserResponse(UserCreate):
    id: str

    model_config = {
        "from_attributes": True  # Pydantic v2 compatible
    }

# Optional: list of users response
class UsersListResponse(BaseModel):
    users: List[UserResponse]