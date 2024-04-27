from redis.asyncio import Redis

from core.config import settings
from repositories.redis_repository import RedisRepository

redis: RedisRepository | None


async def get_redis() -> RedisRepository:
    client = Redis(
        host=settings.redis.redis_host,
        port=settings.redis.redis_port,
        db=settings.redis.redis_database,
    )
    return RedisRepository(connection=client)
