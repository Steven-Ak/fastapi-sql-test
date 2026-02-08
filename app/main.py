from fastapi import FastAPI
from app.api.v1.router import router
from app.core.database import engine, Base

from app.models import item, user, user_item

Base.metadata.create_all(bind=engine)

app = FastAPI(title="FastAPI CRUD Clean Architecture")

app.include_router(router)