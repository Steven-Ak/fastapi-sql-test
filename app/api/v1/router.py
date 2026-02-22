from fastapi import APIRouter
from app.api.v1 import item_router, user_router, user_item_router, auth_router

router = APIRouter()
router.include_router(item_router.router)
router.include_router(user_router.router)
router.include_router(user_item_router.router)
router.include_router(auth_router.router)