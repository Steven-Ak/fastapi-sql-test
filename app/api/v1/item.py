from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.schemas.item import ItemCreate, ItemResponse
from app.core.database import get_db
from app.repositories.item import ItemRepository
from app.services.item import ItemService

router = APIRouter(prefix="/items", tags=["Items"])

@router.post("", response_model=ItemResponse)
def create(item: ItemCreate, db: Session = Depends(get_db)):
    service = ItemService(ItemRepository(db))
    return service.create_item(item)

@router.get("", response_model=List[ItemResponse])
def read_all(db: Session = Depends(get_db)):
    service = ItemService(ItemRepository(db))
    return service.get_items()

@router.get("/{item_id}", response_model=ItemResponse)
def read_one(item_id: int, db: Session = Depends(get_db)):
    service = ItemService(ItemRepository(db))
    try:
        return service.get_item(item_id)
    except ValueError:
        raise HTTPException(404, "Item not found")

@router.put("/{item_id}", response_model=ItemResponse)
def update(item_id: int, item: ItemCreate, db: Session = Depends(get_db)):
    service = ItemService(ItemRepository(db))
    try:
        return service.update_item(item_id, item)
    except ValueError:
        raise HTTPException(404, "Item not found")

@router.delete("/{item_id}")
def delete(item_id: int, db: Session = Depends(get_db)):
    service = ItemService(ItemRepository(db))
    try:
        service.delete_item(item_id)
        return {"message": "Item deleted"}
    except ValueError:
        raise HTTPException(404, "Item not found")