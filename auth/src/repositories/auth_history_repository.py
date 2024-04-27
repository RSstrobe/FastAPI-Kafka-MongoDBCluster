import datetime
import uuid

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from helpers.pagination import get_pagination_parameters
from repositories.sqlalchemy_repository import SQLAlchemyRepository
from models.auth_orm_models import AuthHistotyOrm
from schemas import histories
from schemas.histories import FullIdHistorySchema, FullHistorySchema
from db.sqlalchemy_db import get_db_session


class AuthHistoryRepository(SQLAlchemyRepository):
    _model = AuthHistotyOrm

    def __init__(self, session: AsyncSession):
        super().__init__(session=session)

    async def get_auth_history(
        self, user_id: str, history_data: histories.HistoryRequestSchema
    ) -> list[FullHistorySchema]:
        offset_num, limit_num = get_pagination_parameters(
            history_data.page_size, history_data.page_number
        )
        self._statement = (
            select(self._model)
            .where(self._model.user_id == user_id)
            .order_by(self._model.dt_login.desc())
            .offset(offset_num)
            .limit(limit_num)
        )
        raw_result = await self.read()
        result = [
            self.to_pydantic(db_obj=row, pydantic_model=FullHistorySchema)
            for row in raw_result
        ]
        return result

    async def get_total_records(self, user_id: str) -> int:
        self._statement = (
            select(func.count())
            .select_from(self._model)
            .where(self._model.user_id == user_id)
        )
        raw_result = await self.read_one()
        return raw_result

    async def add_login_history(self, user_id: uuid.UUID, device_id: str):
        session = uuid.uuid4()
        auth_history = FullIdHistorySchema(
            id=session,
            user_id=user_id,
            dt_login=datetime.datetime.now(),
            dt_logout=None,
            device_id=device_id,
        )
        await self.create(auth_history.dict())
        return session

    async def add_logout_history(self, session_id: uuid.UUID):
        update_data = {"dt_logout": datetime.datetime.now()}
        await self.update(
            orm_field=self._model.id, where_cond=session_id, update_data=update_data
        )


def get_db_history_client(session: AsyncSession = Depends(get_db_session)):
    return AuthHistoryRepository(session=session)
