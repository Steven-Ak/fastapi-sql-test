from fastapi import APIRouter, Depends
from typing import List
from app.models.user_model import User

from app.api.auth_deps import get_current_user
from app.schemas.user_schema import UserCreate, UserResponse, UserUpdate
from app.services.user_service import UserService
from app.api.service_deps import get_user_service

router = APIRouter(prefix="/users", tags=["Users"], dependencies=[Depends(get_current_user)])

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

@router.get("/", response_model=UserResponse)  ############################# Check
def read_one(
    service: UserService = Depends(get_user_service),
    user: User = Depends(get_current_user)
):
    return service.get_user(user.id)

@router.put("/", response_model=UserResponse)
def update(
    user: UserCreate,
    service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user)
):
    return service.update_user(current_user.user_id, user, current_user)

@router.patch("/", response_model=UserResponse)
def patch(
    user: UserUpdate,
    service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user)
):
    return service.patch_user(current_user.id, user, current_user)

@router.delete("/")
def delete(
    service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user)
):
    
    service.delete_user(current_user.id, current_user)
    return {"message": "User deleted"}