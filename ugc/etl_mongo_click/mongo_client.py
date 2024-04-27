from pymongo import MongoClient

from config import settings


def get_mongo_client():
    return MongoClient(
        host=settings.mongo_host,
        port=settings.mongo_port,
        uuidRepresentation='standard'
    )
