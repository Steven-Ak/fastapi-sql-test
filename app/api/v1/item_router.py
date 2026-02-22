from fastapi import APIRouter, Depends
from typing import List

from app.schemas.item_schema import ItemCreate, ItemResponse, ItemUpdate
from app.services.item_service import ItemService
from app.api.service_deps import get_item_service

router = APIRouter(prefix="/items", tags=["Items"])

@router.post("", response_model=ItemResponse)
def create(
    item: ItemCreate,
    service: ItemService = Depends(get_item_service),
):
    return service.create_item(item)

@router.get("", response_model=List[ItemResponse])
def read_all(
    service: ItemService = Depends(get_item_service),
):
    return service.get_items()

@router.get("/{item_id}", response_model=ItemResponse)
def read_one(
    item_id: int,
    service: ItemService = Depends(get_item_service),
):
    return service.get_item(item_id)

@router.put("/{item_id}", response_model=ItemResponse)
def update(
    item_id: int,
    item: ItemCreate,
    service: ItemService = Depends(get_item_service),
):
    return service.update_item(item_id, item)

@router.patch("/{item_id}", response_model=ItemResponse)
def patch(
    item_id: int,
    item: ItemUpdate,
    service: ItemService = Depends(get_item_service),
):
    return service.patch_item(item_id, item)

@router.delete("/{item_id}")
def delete(
    item_id: int,
    service: ItemService = Depends(get_item_service),
):
    service.delete_item(item_id)
    return {"message": "Item deleted"}
