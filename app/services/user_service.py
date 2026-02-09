from app.services.base_service import BaseService
from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import UserCreate
from app.models.user_model import User
from sqlalchemy.exc import IntegrityError
from app.core.exceptions import DuplicateException

class UserService(BaseService[User]):
    def __init__(self, repo: UserRepository):
        super().__init__(repo, User)

    def create_user(self, data: UserCreate):
        try:
            user = User(**data.model_dump())
            return self.repo.create(user)
        except IntegrityError:
            raise DuplicateException("User", "username or email")

    def get_users(self):
        return self.get_all()
    
    def get_user(self, user_id: int):
        return self.get_by_id(user_id)

    def update_user(self, user_id: int, data: UserCreate):
        user = self.get_by_id(user_id)
        user.username = data.username
        user.email = data.email
        user.full_name = data.full_name
        try:
            return self.repo.update(user)
        except IntegrityError:
            raise DuplicateException("User", "username or email")
    
    def delete_user(self, user_id: int):
        return self.delete(user_id)