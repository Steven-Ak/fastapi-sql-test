from app.repositories.user import UserRepository

class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def create_user(self, user_data: dict):
        return await self.repo.create(user_data)

    async def get_users(self):
        return await self.repo.get_all()

    async def get_user(self, user_id: str):
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        return user

    async def update_user(self, user_id: str, user_data: dict):
        modified = await self.repo.update(user_id, user_data)
        if modified == 0:
            raise ValueError("User not found or not updated")
        return {"id": user_id, **user_data}

    async def delete_user(self, user_id: str):
        deleted = await self.repo.delete(user_id)
        if deleted == 0:
            raise ValueError("User not found")
        return {"id": user_id}