from uuid import UUID
from pydantic import Field, EmailStr
from .base import BaseSchema


class UserBaseSchema(BaseSchema):
    email: EmailStr


class LoginUserSchema(UserBaseSchema):
    hashed_password: str


class ChangePasswordSchema(BaseSchema):
    old_password: str
    new_password: str


class RefreshTokenUserSchema(BaseSchema):
    refresh_token: str


class LoginUserResponseSchema(RefreshTokenUserSchema):
    access_token: str


class FullUserSchema(UserBaseSchema):
    user_name: str | None = Field(default=None)
    first_name: str | None = Field(default=None)
    last_name: str | None = Field(default=None)
    phone_number: str | None = Field(default=None)


class CreateUserSchema(LoginUserSchema, FullUserSchema):
    pass


class MainInfoUserSchema(LoginUserSchema):
    id: UUID


class FullInfoUserSchema(CreateUserSchema, MainInfoUserSchema):
    pass
