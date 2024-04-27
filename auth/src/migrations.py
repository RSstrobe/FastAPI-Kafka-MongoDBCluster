import os
from pathlib import Path
from types import SimpleNamespace

from alembic.command import upgrade
from alembic.config import Config

from core.config import settings

PROJECT_PATH = Path(__file__).parent.resolve().parent


def make_alembic_config(
    cmd_opts: SimpleNamespace, base_path: str = PROJECT_PATH
) -> Config:
    if not os.path.isabs(cmd_opts.config):
        cmd_opts.config = os.path.join(base_path, cmd_opts.config)

    config = Config(file_=cmd_opts.config, ini_section=cmd_opts.name, cmd_opts=cmd_opts)

    alembic_location = config.get_main_option("script_location")
    if not os.path.isabs(alembic_location):
        config.set_main_option(
            "script_location", os.path.join(base_path, alembic_location)
        )
    if cmd_opts.pg_url:
        config.set_main_option("sqlalchemy.url", cmd_opts.pg_url)

    return config


def alembic_config_from_url(pg_url: str | None = None) -> Config:
    cmd_options = SimpleNamespace(
        config="alembic.ini",
        name="alembic",
        pg_url=pg_url,
        raiseerr=False,
        x=None,
    )

    return make_alembic_config(cmd_options)


def migrated_postgres(pg_url: str | None = None) -> None:
    alembic_config = alembic_config_from_url(pg_url)
    upgrade(alembic_config, "head")


if __name__ == "__main__":
    pg_url = settings.postgres.database_url_asyncpg + "?async_fallback=True"
    migrated_postgres(pg_url)
