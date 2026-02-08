from fastapi import APIRouter, Depends
from typing import List

from app.schemas.user_schema import UserCreate, UserResponse
from app.services.user_service import UserService
from app.api.service_deps import get_user_service

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("", response_model=UserResponse)
def create(
    user: UserCreate,
    service: UserService = Depends(get_user_service),
):
    return service.create_user(user)

@router.get("", response_model=List[UserResponse])
def read_all(
    service: UserService = Depends(get_user_service),
):
    return service.get_users()

@router.get("/{user_id}", response_model=UserResponse)
def read_one(
    user_id: int,
    service: UserService = Depends(get_user_service),
):
    return service.get_user(user_id)

@router.put("/{user_id}", response_model=UserResponse)
def update(
    user_id: int,
    user: UserCreate,
    service: UserService = Depends(get_user_service),
):
    return service.update_user(user_id, user)

@router.delete("/{user_id}")
def delete(
    user_id: int,
    service: UserService = Depends(get_user_service),
):
    service.delete_user(user_id)
    return {"message": "User deleted"}