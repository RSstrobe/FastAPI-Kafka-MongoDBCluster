from collections.abc import AsyncGenerator

from sqlalchemy import exc
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from core.config import settings

engine = create_async_engine(settings.postgres.database_url_asyncpg)
async_factory = async_sessionmaker(engine)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_factory() as session:
        try:
            yield session
            await session.commit()
        except exc.SQLAlchemyError as error:
            await session.rollback()
            raise error
