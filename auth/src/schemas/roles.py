import uuid

from pydantic import BaseModel, Field, EmailStr


class MixinId(BaseModel):
    id: uuid.UUID = Field(title="ID", default_factory=uuid.uuid4)


class RoleSchemaDto(BaseModel):
    role_name: str = Field(title="Имя роли", max_length=50)
    comment: str = Field(title="Комментарий", max_length=256)


class RoleSchema(RoleSchemaDto, MixinId):
    pass


class ActionSchema(BaseModel):
    action_name: str = Field(title="Имя действия", max_length=50)
    comment: str | None = Field(title="Комментарий", max_length=256)


class UserRoleSchema(BaseModel):
    user_id: uuid.UUID = Field(title="ID пользователя")
    role_id: uuid.UUID = Field(title="ID роли")


class UserRoleDto(BaseModel):
    user_email: EmailStr = Field(title="Email пользователя")
    role_name: str = Field(title="Имя роли", max_length=50)


class UserRole(UserRoleSchema, MixinId):
    pass


class RoleActionSchema(RoleSchemaDto):
    actions: list[ActionSchema]


class ActionDto(BaseModel):
    logout: bool = Field(default=True)
    refresh_token: bool = Field(default=True)
    history: bool = Field(default=True)
    change_password: bool = Field(default=True)
    create_role: bool = Field(default=False)
    delete_role: bool = Field(default=False)
    change_role: bool = Field(default=False)
    get_roles: bool = Field(default=False)
    set_role: bool = Field(default=False)
    grab_role: bool = Field(default=False)
    check_role: bool = Field(default=False)


class RoleActionDto(RoleSchemaDto):
    actions: list[ActionDto]


class RoleAction(RoleActionDto, MixinId):
    pass


class MixActionsSchema(MixinId):
    role_id: uuid.UUID
    action_id: uuid.UUID
