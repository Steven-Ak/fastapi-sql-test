from app.repositories.user import UserRepository
from app.schemas.user import UserCreate
from app.models.user import User

class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def create_user(self, data: UserCreate):
        user = User(**data.model_dump())
        return self.repo.create(user)

    def get_users(self):
        return self.repo.get_all()

    def get_user(self, user_id: int):
        user = self.repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        return user
    
    def update_user(self, user_id: int, user_data: UserCreate):
        user = self.repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        user.name = user_data.name
        user.description = user_data.description
        return self.repo.update(user)

    def delete_user(self, user_id: int):
        user = self.repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        self.repo.delete(user)
        return True