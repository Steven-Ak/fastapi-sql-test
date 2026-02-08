from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.schemas.user import UserCreate, UserResponse
from app.core.database import get_db
from app.repositories.user import UserRepository
from app.services.user import UserService

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("", response_model=UserResponse)
def create(user: UserCreate, db: Session = Depends(get_db)):
    service = UserService(UserRepository(db))
    return service.create_user(user)

@router.get("", response_model=List[UserResponse])
def read_all(db: Session = Depends(get_db)):
    service = UserService(UserRepository(db))
    return service.get_users()

@router.get("/{user_id}", response_model=UserResponse)
def read_one(user_id: int, db: Session = Depends(get_db)):
    service = UserService(UserRepository(db))
    try:
        return service.get_user(user_id)
    except ValueError:
        raise HTTPException(404, "User not found")
    
@router.put("/{user_id}", response_model=UserResponse)
def update(user_id: int, user: UserCreate, db: Session = Depends(get_db)):
    service = UserService(UserRepository(db))
    try:
        return service.update_user(user_id, user)
    except ValueError:
        raise HTTPException(404, "User not found")

@router.delete("/{user_id}")
def delete(user_id: int, db: Session = Depends(get_db)):
    service = UserService(UserRepository(db))
    try:
        service.delete_user(user_id)
        return {"message": "User deleted"}
    except ValueError:
        raise HTTPException(404, "User not found")