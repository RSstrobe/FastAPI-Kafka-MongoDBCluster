from motor.motor_asyncio import AsyncIOMotorClient

from db.mongo import get_mongo_client
from repositories.base import BaseRepository


class MongoBeanieRepository(BaseRepository):
    def __init__(self, client: AsyncIOMotorClient, collection: str):
        self.mongo_collection = client["ugc"][collection]

    async def create(self, document: dict):
        await self.mongo_collection.insert_one(document)

    async def read(self, document: dict, skip: int = 0, limit: int = 100, sort_by: str = "", sort_method: int = -1):
        if sort_by:
            response = self.mongo_collection.find(document).sort([(sort_by, sort_method)]).skip(skip).limit(limit)
        else:
            response = self.mongo_collection.find(document).skip(skip).limit(limit)
        return await response.to_list(length=None)

    async def update(self, filter_data: dict, update_data: dict):
        await self.mongo_collection.find_one_and_update(
            filter_data, {"$set": update_data}
        )

    async def delete(self, document: dict):
        await self.mongo_collection.delete_one(document)

    async def count(self, document: dict):
        return await self.mongo_collection.count_documents(document)


def get_mongo_repo(collection: str, client: AsyncIOMotorClient = get_mongo_client()):
    return MongoBeanieRepository(client=client, collection=collection)
