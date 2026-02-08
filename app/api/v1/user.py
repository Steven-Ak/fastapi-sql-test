from fastapi import APIRouter, HTTPException
from typing import List
from app.repositories.user import UserRepository
from app.services.user import UserService
from app.schemas.user import UserCreate, UserResponse

router = APIRouter(prefix="/users", tags=["Users"])

repo = UserRepository()
service = UserService(repo)

# CREATE
@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate):
    return await service.create_user(user.model_dump())

# READ ALL
@router.get("/", response_model=List[UserResponse])
async def read_users():
    return await service.get_users()

# READ ONE
@router.get("/{user_id}", response_model=UserResponse)
async def read_user(user_id: str):
    try:
        return await service.get_user(user_id)
    except ValueError:
        raise HTTPException(404, "User not found")

# UPDATE
@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, user: UserCreate):
    try:
        return await service.update_user(user_id, user.dict())
    except ValueError:
        raise HTTPException(404, "User not found")

# DELETE
@router.delete("/{user_id}")
async def delete_user(user_id: str):
    try:
        await service.delete_user(user_id)
        return {"message": "User deleted"}
    except ValueError:
        raise HTTPException(404, "User not found")