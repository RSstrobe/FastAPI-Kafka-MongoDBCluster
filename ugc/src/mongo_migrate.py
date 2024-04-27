import asyncio
from helpers.mongo_init import get_mongodb_init


async def mongo_run_migration():
    mongo_init = get_mongodb_init()
    await mongo_init.create_collections()

if __name__ == "__main__":
    asyncio.run(mongo_run_migration())