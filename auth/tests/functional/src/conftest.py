import asyncio
import json

import aiohttp
import pytest_asyncio
from alembic.command import upgrade
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from yarl import URL

from tests.functional.core.settings import test_settings
from tests.functional.utils.db_helpers import drop_all_tables


@pytest_asyncio.fixture(scope="session", autouse=True)
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
def pg_migrate(alembconfig_from_url):
    drop_all_tables()
    upgrade(alembconfig_from_url, "head")


@pytest_asyncio.fixture(name="aiohttp_session", scope="session")
async def aiohttp_session():
    jar = aiohttp.CookieJar(unsafe=False)
    connector = aiohttp.TCPConnector(force_close=True)
    session = aiohttp.ClientSession(connector=connector, cookie_jar=jar)
    yield session
    await session.close()


@pytest_asyncio.fixture(name="sqlalchemy_session", scope="session")
async def sqlalchemy_session():
    engine = create_async_engine(test_settings.database_url_asyncpg)
    async_factory = async_sessionmaker(engine)
    async with async_factory() as session:
        yield session


@pytest_asyncio.fixture(name="redis_client", scope="session")
async def redis_client():
    redis_client = Redis(
        host=test_settings.redis_host,
        port=test_settings.redis_port,
        db=test_settings.redis_database,
    )
    yield redis_client
    await redis_client.close()


@pytest_asyncio.fixture(name="redis_read_data", scope="session")
def redis_read_data(redis_client):
    async def inner(key: str):
        data = await redis_client.smembers(str(key))
        if not data:
            return None

        return data

    return inner


@pytest_asyncio.fixture(name="make_get_request", scope="session")
def make_get_request(aiohttp_session):
    async def inner(url: str, query_data: dict, cookie=None):
        kwarg = {
            "url": url,
            "params": query_data,
            "raise_for_status": True,
        }
        if cookie:
            kwarg["cookies"] = {
                "access_token": cookie["access_token"].value,
                "refresh_token": cookie["refresh_token"].value,
            }
        async with aiohttp_session.get(**kwarg) as response:
            return await response.json(), response.status, response.cookies

    return inner


@pytest_asyncio.fixture(name="make_post_request")
def make_post_request(aiohttp_session):
    async def inner(url: str, query_data: dict, cookie=None, query_body: dict = None):
        header = {"accept": "application/json", "Content-Type": "application/json"}
        kwarg = {
            "url": url,
            "params": query_data,
            "raise_for_status": True,
            "headers": header,
            "data": json.dumps([query_body]),
        }
        if cookie:
            kwarg["cookies"] = {"refresh_token": cookie["refresh_token"].value}

        async with aiohttp_session.post(**kwarg) as response:
            return await response.json(), response.status, response.cookies

    return inner


@pytest_asyncio.fixture(name="make_put_request")
def make_put_request(aiohttp_session):
    async def inner(url: str, query_data: dict, cookie=None, query_body: dict = None):
        header = {"accept": "application/json", "Content-Type": "application/json"}
        kwarg = {
            "url": str(URL(url).with_query(query_data)).replace("+", ""),
            "raise_for_status": True,
            "headers": header,
            "data": json.dumps([query_body]),
        }
        if cookie:
            kwarg["cookies"] = {"refresh_token": cookie["refresh_token"].value}

        async with aiohttp_session.put(**kwarg) as response:
            return await response.json(), response.status, response.cookies

    return inner


@pytest_asyncio.fixture(name="make_delete_request")
def make_delete_request(aiohttp_session):
    async def inner(url, query_data: dict, cookies=None):
        kwarg = {
            "url": url,
            "params": query_data,
            "raise_for_status": True,
        }
        if cookies:
            kwarg["cookies"] = {"refresh_token": cookies["refresh_token"].value}

        async with aiohttp_session.delete(**kwarg) as response:
            return response.status, response.cookies

    return inner


@pytest_asyncio.fixture(name="execute_raw_sql", scope="session")
def execute_raw_sql(sqlalchemy_session):
    async def inner(sql: str):
        sql_text = text(sql)
        await sqlalchemy_session.execute(sql_text)
        await sqlalchemy_session.commit()

    return inner
