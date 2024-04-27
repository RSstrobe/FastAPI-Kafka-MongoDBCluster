from motor.motor_asyncio import AsyncIOMotorClient

from core.config import settings


def get_mongo_client() -> AsyncIOMotorClient:
    return AsyncIOMotorClient(str(settings.mongodb.mongodb_uri))
