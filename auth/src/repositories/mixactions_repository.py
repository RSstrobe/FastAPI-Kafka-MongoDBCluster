import uuid

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.sqlalchemy_db import get_db_session
from repositories.sqlalchemy_repository import SQLAlchemyRepository
from models.auth_orm_models import MixActionsOrm
from schemas import roles


class MixActionsRepository(SQLAlchemyRepository):
    _model = MixActionsOrm

    def __init__(self, session: AsyncSession):
        super().__init__(session=session)

    async def set_actions_to_role(
        self, role_id: uuid.UUID, action_ids: list[uuid.UUID]
    ):
        for action_id in action_ids:
            mix_actions_model = roles.MixActionsSchema(
                role_id=role_id, action_id=action_id
            )
            await self.create(dict(mix_actions_model))

    async def delete_actions_by_role(self, role_id: uuid.UUID):
        await self.delete(self._model.role_id, role_id)


def get_mix_actions_repository(session: AsyncSession = Depends(get_db_session)):
    return MixActionsRepository(session=session)
