from app.core.config import settings
from app.clients.database_clients.postgres_client import PostgresClient
from app.clients.database_clients.supabase_client import SupabaseClient

# Initialize database clients
postgres_client = PostgresClient(
    connection_string=settings.DATABASE_URL,
    pool_size=5
)

supabase_client = SupabaseClient(
    connection_string=settings.SUPABASE_DB_URL,
    supabase_url=settings.SUPABASE_URL,
    supabase_key=settings.SUPABASE_KEY,
    pool_size=5
)

# Dependency injection functions
def get_postgres_db():
    """Dependency for PostgreSQL database session"""
    yield from postgres_client.get_session()


def get_supabase_db():
    """Dependency for Supabase database session"""
    yield from supabase_client.get_session()


# Default database (for backwards compatibility)
get_db = get_supabase_db


# Cleanup function (optional - for app shutdown)
def close_all_connections():
    """Close all database connections"""
    postgres_client.close()
    supabase_client.close()