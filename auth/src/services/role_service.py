from fastapi import Depends

from helpers.exceptions import (
    AuthRoleIsAlreadySetException,
    AuthRoleIsNotExistException,
    AuthRoleIsExistException,
)
from repositories.actions_repository import ActionsRepository, get_actions_repository
from repositories.mixactions_repository import (
    get_mix_actions_repository,
    MixActionsRepository,
)
from repositories.roles_repository import RolesRepository, get_roles_repository
from repositories.user_data_repository import UserDataRepository, get_database_client
from schemas import roles
from services.base_service import BaseService


class AuthRoleService(BaseService):
    def __init__(
        self,
        users_repo: UserDataRepository,
        roles_repo: RolesRepository,
        mix_actions_repo: MixActionsRepository,
        action_repo: ActionsRepository,
    ):
        self.users_repo = users_repo
        self.roles_repo = roles_repo
        self.mix_actions_repo = mix_actions_repo
        self.action_repo = action_repo

    async def create(self, role: roles.RoleActionDto):
        """Create a new role."""
        role_exist = await self.roles_repo.get_role_by_name(role_name=role.role_name)
        if role_exist:
            raise AuthRoleIsExistException()
        action_names = [i[0] for i in role.actions[0] if i[-1]]
        roles_db_obj = await self.action_repo.get_actions_by_names(action_names)
        roles_ids = [row.id for row in roles_db_obj]
        role_model = roles.RoleSchema(role_name=role.role_name, comment=role.comment)
        await self.roles_repo.create(role_model.dict())
        await self.mix_actions_repo.set_actions_to_role(
            role_id=role_model.id, action_ids=roles_ids
        )
        return role

    async def get(self, *args, **kwargs) -> list[roles.RoleActionSchema] | None:
        result = await self.roles_repo.get_all_roles()
        if not result:
            raise AuthRoleIsNotExistException(detail="Roles are not exist")
        return result

    async def update(self, role: roles.RoleActionDto):
        await self.delete(name=role.role_name)
        db_obj = await self.create(role=role)
        return db_obj

    async def delete(self, name: str) -> None:
        role = await self.roles_repo.get_role_by_name(role_name=name)
        if not role:
            raise AuthRoleIsNotExistException()
        await self.roles_repo.delete(self.roles_repo._model.id, role.id)

    async def set_role(self, user_role: roles.UserRoleDto) -> roles.UserRole | None:
        """Set role for user."""
        is_need_update = await self.verify(user_role=user_role)
        if is_need_update:
            raise AuthRoleIsAlreadySetException()
        role = await self.roles_repo.get_role_by_name(role_name=user_role.role_name)
        if not role:
            raise AuthRoleIsNotExistException()
        user = await self.users_repo.get_user_by_email(email=user_role.user_email)
        db_obj = await self.users_repo.set_role(user_id=user.id, role_id=role.id)
        return db_obj

    async def verify(self, user_role: roles.UserRoleDto) -> bool:
        """Verify role for user."""
        db_role = await self.users_repo.get_role_by_user(user_role=user_role)
        is_verify = False
        if db_role == user_role.role_name:
            is_verify = True
        return is_verify


def get_role_service(
    users_repo: UserDataRepository = Depends(get_database_client),
    roles_repo: RolesRepository = Depends(get_roles_repository),
    mix_actions_repo: MixActionsRepository = Depends(get_mix_actions_repository),
    action_repo: ActionsRepository = Depends(get_actions_repository),
) -> AuthRoleService:
    return AuthRoleService(
        users_repo=users_repo,
        roles_repo=roles_repo,
        mix_actions_repo=mix_actions_repo,
        action_repo=action_repo,
    )
