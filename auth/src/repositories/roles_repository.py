from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from db.sqlalchemy_db import get_db_session
from models.auth_orm_models import RolesOrm, ActionsOrm, MixActionsOrm
from repositories.sqlalchemy_repository import SQLAlchemyRepository
from schemas import roles


class RolesRepository(SQLAlchemyRepository):
    _model = RolesOrm

    def __init__(self, session: AsyncSession):
        super().__init__(session=session)

    async def get_role_by_name(self, role_name: str) -> roles.RoleSchema | None:
        self._statement = select(RolesOrm).where(RolesOrm.role_name == role_name)
        role_orm = await self.read_one()
        role = self.to_pydantic(role_orm, roles.RoleSchema)
        return role

    async def get_all_roles(self) -> list[roles.RoleActionSchema] | None:
        self._statement = (
            select(
                func.json_build_object(
                    "role_name",
                    RolesOrm.role_name,
                    "comment",
                    RolesOrm.comment,
                    "actions",
                    func.array_agg(
                        func.json_build_object(
                            "action_name",
                            ActionsOrm.action_name,
                            "comment",
                            ActionsOrm.comment,
                        )
                    ),
                )
            )
            .join(MixActionsOrm, RolesOrm.id == MixActionsOrm.role_id)
            .join(ActionsOrm, MixActionsOrm.action_id == ActionsOrm.id)
            .group_by(RolesOrm.role_name, RolesOrm.comment)
        )

        raw_result = await self.read()
        result = None
        if raw_result:
            result = [roles.RoleActionSchema(**item) for item in raw_result]
        return result


def get_roles_repository(session: AsyncSession = Depends(get_db_session)):
    return RolesRepository(session=session)
