from fastapi import FastAPI
from app.api.v1.router import router
from app.core.database import engine
from app.models import item

item.Base.metadata.create_all(bind=engine)

app = FastAPI(title="FastAPI CRUD Clean Architcture")

app.include_router(router)