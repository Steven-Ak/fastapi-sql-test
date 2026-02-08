from fastapi import APIRouter, Depends
from typing import List

from app.schemas.user_item_schema import UserItemCreate, UserItemResponse
from app.services.user_item_service import UserItemService
from app.api.service_deps import get_user_item_service

router = APIRouter(prefix="/user-items", tags=["User Items"])

@router.post("", response_model=UserItemResponse)
def assign_item(
    user_item: UserItemCreate,
    service: UserItemService = Depends(get_user_item_service),
):
    return service.assign_item_to_user(user_item)

@router.get("/user/{user_id}", response_model=List[UserItemResponse])
def get_user_items(
    user_id: int,
    service: UserItemService = Depends(get_user_item_service),
):
    return service.get_user_items(user_id)

@router.get("/item/{item_id}", response_model=List[UserItemResponse])
def get_item_users(
    item_id: int,
    service: UserItemService = Depends(get_user_item_service),
):
    return service.get_item_users(item_id)

@router.delete("/{user_item_id}")
def delete_assignment(
    user_item_id: int,
    service: UserItemService = Depends(get_user_item_service),
):
    service.delete(user_item_id)
    return {"message": "User-Item assignment deleted"}