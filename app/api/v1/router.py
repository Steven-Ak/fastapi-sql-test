from fastapi import APIRouter
from app.api.v1 import item, user

router = APIRouter()
router.include_router(item.router)
router.include_router(user.router)