from types import SimpleNamespace

import pytest_asyncio
from alembic.config import Config

from src.migrations import make_alembic_config
from tests.functional.core.settings import test_settings


@pytest_asyncio.fixture(name="alembconfig_from_url", scope="session", autouse=True)
def alembconfig_from_url() -> Config:
    pg_url = test_settings.database_url_asyncpg + "?async_fallback=True"
    cmd_options = SimpleNamespace(
        config="alembic.ini",
        name="alembic",
        pg_url=pg_url,
        raiseerr=False,
        x=None,
    )

    return make_alembic_config(cmd_options)
