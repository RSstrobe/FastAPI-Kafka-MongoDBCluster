import logging
import json

from redis import Redis

from .base_repository import MixinSaveRepository
from core.config import settings

logger = logging.getLogger(__name__)

LIFETIME = settings.redis.redis_time_save_cache


class RedisRepository(MixinSaveRepository):
    redis = Redis | None

    def __init__(self, connection=Redis):
        super().__init__(connection)

    async def get(self, key: str):
        try:
            data = await self.connection.get(str(key))
        except ConnectionError as e:
            data = None
            logger.error(e)

        if not data:
            return None
        return json.loads(data)

    async def save(self, key: str, value: dict):
        try:
            await self.connection.set(str(key), value, ex=LIFETIME)
        except ConnectionError as e:
            logger.error(e)
