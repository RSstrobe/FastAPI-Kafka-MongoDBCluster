import json

from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk
from elasticsearch.exceptions import TransportError

import aiohttp
import asyncio
import pytest_asyncio
from pydantic import BaseModel
from redis.asyncio import Redis

from tests.functional.core.settings import test_settings


@pytest_asyncio.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(name="aiohttp_session", scope="session")
async def aiohttp_session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest_asyncio.fixture(name="es_client", scope="session")
async def es_client():
    es_client = AsyncElasticsearch(
        hosts=[f"{test_settings.elastic_host}:{test_settings.elastic_port}"]
    )
    yield es_client
    await es_client.close()


@pytest_asyncio.fixture(name="redis_client", scope="session")
async def redis_client():
    redis_client = Redis(
        host=test_settings.redis_host,
        port=test_settings.redis_port,
        db=test_settings.redis_database,
    )
    yield redis_client
    await redis_client.close()


@pytest_asyncio.fixture(name="es_write_data")
def es_write_data(es_client):
    async def inner(data: list[dict], index: str, index_mapping: dict):
        if await es_client.indices.exists(index=index):
            await es_client.indices.delete(index=index)
        await es_client.indices.create(index=index, body=index_mapping)

        updated, errors = await async_bulk(
            client=es_client, actions=data, refresh="wait_for"
        )

        if errors:
            raise TransportError("Ошибка записи данных в Elasticsearch")

    return inner


@pytest_asyncio.fixture(name="redis_read_data")
def redis_read_data(redis_client):
    async def inner(key: str):
        data = await redis_client.get(str(key))
        if not data:
            return None

        return json.loads(data)

    return inner


@pytest_asyncio.fixture(name="make_get_request")
def make_get_request(aiohttp_session):
    async def inner(url: str, query_data: dict):
        async with aiohttp_session.get(
            url, params=query_data, raise_for_status=True
        ) as response:
            return await response.json(), response.status

    return inner


@pytest_asyncio.fixture(name="generate_data")
def generate_data():
    def inner(data: list[dict], index: str, model: BaseModel):
        bulk_query: list[dict] = []
        for row in data:
            data = {"_index": index, "_id": row["id"]}
            data.update({"_source": model(**row).json()})
            bulk_query.append(data)

        return bulk_query

    return inner
