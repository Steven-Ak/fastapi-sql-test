from app.services.base_service import BaseService
from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import UserCreate, UserUpdate
from app.models.user_model import User
from app.core.security import get_password_hash, verify_password
from sqlalchemy.exc import IntegrityError
from app.core.exceptions import DuplicateException, UnauthorizedException, ForbiddenException, NotFoundException
from fastapi import HTTPException, status

class UserService(BaseService[User]):
    def __init__(self, repo: UserRepository):
        super().__init__(repo, User)

    def create_user(self, data: UserCreate):
        try:
            user = User(
                username=data.username,
                email=data.email,
                full_name=data.full_name,
                password_hash=get_password_hash(data.password)
            )
            return self.repo.create(user)
        except IntegrityError:
            raise DuplicateException("User", "username or email")

    def authenticate_user(self, username: str, password: str):
        user = self.repo.get_by_username(username)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    def get_users(self):
        return self.get_all()
    
    def get_user(self, user_id: int):
        return self.get_by_id(user_id)
    
    def get_user_by_username(self, username: str):
        return self.repo.get_by_username(username)

    def update_user(self, user_id: int, data: UserCreate, current_user: User):
        user = self.get_by_id(user_id)
        
        # Security: Users can only update their own account
        if user.id != current_user.id:
            raise ForbiddenException("You can only update your own account")
        
        user.username = data.username
        user.email = data.email
        user.full_name = data.full_name
        user.password_hash = get_password_hash(data.password)
        
        try:
            return self.repo.update(user)
        except IntegrityError:
            raise DuplicateException("User", "username or email")
        
    def patch_user(self, user_id: int, data: UserUpdate, current_user: User):
        user = self.get_by_id(user_id)
        
        # Security: Users can only update their own account
        if user.id != current_user.id:
            raise ForbiddenException("You can only update your own account")
        
        # Update only provided fields
        if data.username is not None:
            user.username = data.username
        if data.email is not None:
            user.email = data.email
        if data.full_name is not None:
            user.full_name = data.full_name
        if data.password is not None:
            user.password_hash = get_password_hash(data.password)
        
        try:
            return self.repo.update(user)
        except IntegrityError:
            raise DuplicateException("User", "username or email")
    
    def delete_user(self, user_id: int, current_user: User):
        if user_id != current_user.id:
            raise ForbiddenException("You can only delete your own account")
        
        user = self.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")
        
        self.repo.delete(user)