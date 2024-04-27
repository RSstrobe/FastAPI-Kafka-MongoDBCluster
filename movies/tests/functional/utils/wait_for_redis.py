from redis import Redis
from redis.exceptions import ConnectionError

from subsidiary.backoff import backoff


@backoff(connect_exception=ConnectionError)
def pinging_redis(redis_client: Redis) -> bool:
    """Waiting for test Redis service response"""
    return redis_client.ping()


if __name__ == "__main__":
    client = Redis("redis")
    pinging_redis(redis_client=client)
