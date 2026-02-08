from app.core.mongo import db
from bson import ObjectId

class UserRepository:
    def __init__(self):
        self.collection = db["users"]

    async def create(self, user_data: dict):
        result = await self.collection.insert_one(user_data)
        return {"id": str(result.inserted_id), **user_data}

    async def get_all(self):
        cursor = self.collection.find({})
        users = await cursor.to_list(length=100)
        # convert ObjectId to string
        return [{"id": str(u["_id"]), **{k:v for k,v in u.items() if k!="_id"}} for u in users]

    async def get_by_id(self, user_id: str):
        user = await self.collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            return None
        return {"id": str(user["_id"]), **{k:v for k,v in user.items() if k!="_id"}}

    async def update(self, user_id: str, user_data: dict):
        result = await self.collection.update_one(
            {"_id": ObjectId(user_id)}, {"$set": user_data}
        )
        return result.modified_count

    async def delete(self, user_id: str):
        result = await self.collection.delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count