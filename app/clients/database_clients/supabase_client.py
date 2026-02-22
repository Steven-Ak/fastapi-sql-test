from typing import Generator, Optional
from sqlalchemy.orm import Session
from app.clients.database_clients.db_base_client import BaseDatabaseClient


class SupabaseClient(BaseDatabaseClient):
    """Supabase PostgreSQL database client"""
    
    def __init__(
        self, 
        connection_string: str, 
        supabase_url: Optional[str] = None,
        supabase_key: Optional[str] = None,
        **kwargs
    ):
        super().__init__(connection_string, **kwargs)
        self.db_type = "supabase"
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
    
    def get_session(self) -> Generator[Session, None, None]:
        """Get Supabase database session"""
        db = self.SessionLocal()
        try:
            # You can add Supabase-specific configuration here if needed
            # For example, setting row-level security policies
            yield db
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    def __repr__(self):
        return f"SupabaseClient(url='{self.supabase_url}')"