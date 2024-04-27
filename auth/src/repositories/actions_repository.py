from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.sqlalchemy_db import get_db_session
from repositories.sqlalchemy_repository import SQLAlchemyRepository
from models.auth_orm_models import ActionsOrm


class ActionsRepository(SQLAlchemyRepository):
    _model = ActionsOrm

    def __init__(self, session: AsyncSession):
        super().__init__(session=session)

    async def get_actions_by_names(self, action_names: list[str]):
        self._statement = select(self._model).where(
            self._model.action_name.in_(action_names)
        )
        result = await self.read()
        return result


def get_actions_repository(session: AsyncSession = Depends(get_db_session)):
    return ActionsRepository(session=session)
