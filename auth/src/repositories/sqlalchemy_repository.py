from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Select, Update, update, delete, Delete
from repositories.base import (
    MixinDeleteRepository,
    MixinCreateRepository,
    MixinUpdateRepository,
)


class SQLAlchemyRepository(
    MixinCreateRepository, MixinDeleteRepository, MixinUpdateRepository
):
    _model = None
    _statement: Select | Update | Delete | None = None

    def __init__(self, session: AsyncSession):
        self.session = session

    def reset_statement(self):
        self._statement = None

    @staticmethod
    def to_pydantic(db_obj, pydantic_model):
        try:
            pd_model = pydantic_model(**db_obj.__dict__)
        except (TypeError, AttributeError):
            pd_model = None
        return pd_model

    async def read(self):
        try:
            buff_result = await self.session.execute(self._statement)
            result = buff_result.scalars().all()
        except NoResultFound:
            result = None
        finally:
            await self.session.close()
            self.reset_statement()
        return result

    async def read_one(self):
        try:
            buff_result = await self.session.execute(self._statement)
            result = buff_result.scalars().one()
        except NoResultFound:
            result = None
        finally:
            await self.session.close()
            self.reset_statement()
        return result

    async def delete(self, where_cond, orm_field):
        self._statement = delete(self._model).where(where_cond == orm_field)
        await self.session.execute(self._statement)
        await self.session.commit()

    async def update(self, orm_field, where_cond, update_data):
        self._statement = (
            update(self._model).where(where_cond == orm_field).values(**update_data)
        )
        await self.session.execute(self._statement)
        await self.session.commit()

    async def create(self, entity_model: dict):
        db_obj = self._model(**entity_model)
        self.session.add(db_obj)
        await self.session.flush()
        await self.session.commit()
        return db_obj

    async def merge(self, update_data: dict) -> _model:
        db_obj = await self.session.merge(self._model(**update_data))
        await self.session.commit()
        return db_obj
