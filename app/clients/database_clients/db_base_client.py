from abc import ABC, abstractmethod
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base

# Shared base for all models
Base = declarative_base()


class BaseDatabaseClient(ABC):
    """Abstract base class for database clients"""
    
    def __init__(self, connection_string: str, pool_size: int = 5, **kwargs):
        self.connection_string = connection_string
        self.engine = create_engine(
            connection_string,
            future=True,
            pool_pre_ping=True,
            pool_size=pool_size,
            max_overflow=10,
            **kwargs
        )
        self.SessionLocal = sessionmaker(
            bind=self.engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False
        )
    
    @abstractmethod
    def get_session(self) -> Generator[Session, None, None]:
        """Get database session"""
        pass
    
    def create_tables(self):
        """Create all tables defined in models"""
        Base.metadata.create_all(bind=self.engine)
    
    def drop_tables(self):
        """Drop all tables"""
        Base.metadata.drop_all(bind=self.engine)
    
    def close(self):
        """Close database connections"""
        self.engine.dispose()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()