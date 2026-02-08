from fastapi import FastAPI
from app.api.v1.router import router
from app.core.database import engine, Base

from app.models import item_model, user_item_model, user_model

Base.metadata.create_all(bind=engine)

app = FastAPI(title="FastAPI CRUD Clean Architecture")

app.include_router(router)