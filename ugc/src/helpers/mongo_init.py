from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from db.mongo import get_mongo_client
from helpers import logger
from models.mongo.collections import Review, Evaluation, Bookmark

mongo_logger = logger.UGCLogger()


class MongoDBInit:
    def __init__(self, mongodb_client: AsyncIOMotorClient):
        self.client = mongodb_client

    async def create_collections(self):
        await init_beanie(
            database=self.client.ugc, document_models=[Review, Evaluation, Bookmark]
        )


def get_mongodb_init() -> MongoDBInit:
    return MongoDBInit(mongodb_client=get_mongo_client())
