from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.api.routers.router import router
from app.clients.database_clients import postgres_client, supabase_client, close_all_connections

from app.models import item_model, user_item_model, user_model, chat_model


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables

    
    try:
        supabase_client.create_tables()
        print("✅ Supabase tables created")
    except Exception as e:
        print(f"⚠️  Supabase not available: {e}")
    
    yield
    
    # Shutdown: Close connections
    close_all_connections()
    print("✅ Database connections closed")


app = FastAPI(
    title="FastAPI Test Project",
    lifespan=lifespan
)

app.include_router(router)