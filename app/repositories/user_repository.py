from sqlalchemy.orm import Session
from app.repositories.base_repository import BaseRepository
from app.models.user_model import User

class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session):
        super().__init__(db, User)

    def get_by_email(self, email: str):
        return self.db.query(User).filter(User.email == email).first()
    
    def get_by_username(self, username: str):
        return self.db.query(User).filter(User.username == username).first()