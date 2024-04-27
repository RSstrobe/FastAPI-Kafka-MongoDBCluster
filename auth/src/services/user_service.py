from http.client import HTTPException

from pydantic import EmailStr
from fastapi import Depends, HTTPException, status  # noqa

from .base_service import BaseService
from repositories.user_data_repository import get_database_client, UserDataRepository
from helpers.password import verify_password, get_password_hash


class AuthUserService(BaseService):
    def __init__(self, database_client: UserDataRepository):
        self.database_client = database_client

    async def get(self, *, email: EmailStr):
        """Get user information by email."""
        return await self.database_client.get_user_by_email(email)

    async def get_by_username(self, *, username: str):
        return await self.database_client.get_user_by_username(username)

    async def create(self, user_dto) -> dict:
        """Create a new user by requesting email and password."""

        if not "".join(user_dto.hashed_password.split()):
            raise HTTPException(
                detail="Password must be set.",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        request_email = await self.get(email=user_dto.email)
        if request_email:
            raise HTTPException(
                detail="User already exists",
                status_code=status.HTTP_409_CONFLICT,
            )
        if user_dto.user_name:
            request_username = await self.get_by_username(
                username=user_dto.user_name
            )
            if request_username:
                raise HTTPException(
                    detail="Username already exists.",
                    status_code=status.HTTP_409_CONFLICT,
                )

        user_dto.hashed_password = get_password_hash(user_dto.hashed_password)
        encoded_user = await self.database_client.create_user(user_data=user_dto)
        return encoded_user

    async def delete(self):
        """Delete user by email and password."""
        pass

    async def update(self, user_id: str, password_data):
        """Update user information."""
        response = await self.database_client.get_user_by_id(user_id=user_id)
        if not verify_password(password_data.old_password, response.hashed_password):
            raise HTTPException(
                detail="Invalid login or password.",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
        new_hashed_password = get_password_hash(password_data.new_password)
        await self.database_client.update_password(user_id, new_hashed_password)

    async def check_user(self, user_info):
        response = await self.get(email=user_info.email)
        if not response:
            return None
        if not verify_password(
            user_info.hashed_password,
            response.hashed_password,
        ):
            return None
        return response

    async def get_role(self, user_dto):
        user_id = user_dto.id
        response = await self.database_client.get_role_bu_user_id(user_id)
        return response


def get_user_service(
    database_client: UserDataRepository = Depends(get_database_client),
):
    return AuthUserService(database_client=database_client)
