from typing import Generator
from sqlalchemy.orm import Session
from app.clients.database_clients.db_base_client import BaseDatabaseClient


class PostgresClient(BaseDatabaseClient):
    """Local PostgreSQL database client"""
    
    def __init__(self, connection_string: str, **kwargs):
        super().__init__(connection_string, **kwargs)
        self.db_type = "postgres"
    
    def get_session(self) -> Generator[Session, None, None]:
        """Get PostgreSQL database session"""
        db = self.SessionLocal()
        try:
            yield db
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    def __repr__(self):
        return f"PostgresClient(connection='{self.connection_string}')"