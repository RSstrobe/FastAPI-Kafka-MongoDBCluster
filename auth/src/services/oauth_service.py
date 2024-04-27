from functools import lru_cache

from pydantic import EmailStr
from fastapi import HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.oauth import SocialNetworks
from models.auth_orm_models import UserDataOrm
from schemas.users import CreateUserSchema
from db.sqlalchemy_db import get_db_session
from helpers.random import get_random_string
from .user_service import AuthUserService, get_user_service


class OAuthService:
    def __init__(self, database_client: AsyncSession, user_service: AuthUserService):
        self.database_client = database_client
        self.user_service = user_service

    async def get_user(
            self,
            social_id: str,
            social_name: str,
            email: EmailStr,
            name: str | None = None,
    ):
        response = await self.database_client.execute(
            select(SocialNetworks).where(
                SocialNetworks.social_network_id == social_id,
                SocialNetworks.social_networks_name == social_name,
            )
        )
        social_account = response.scalars().first()
        if social_account:
            response = await self.database_client.execute(
                select(UserDataOrm).where(UserDataOrm.id == social_account.user_id)
            )
            response = response.scalars().first()
            return response

        response = await self.database_client.execute(
            select(UserDataOrm).where(UserDataOrm.email == email)
        )

        user_data = response.scalars().first()
        if not user_data:
            if not email:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Email or password don`t set",
                )

            user = await self.user_service.create(
                CreateUserSchema(
                    email=email,
                    user_name=name,
                    hashed_password=get_random_string(50),
                )
            )

            social_account = SocialNetworks(
                user_id=user["id"],
                social_network_id=social_id,
                social_networks_name=social_name,
                social_network_email=email
            )
            self.database_client.add(social_account)
            await self.database_client.commit()
            return user


@lru_cache
def get_oauth_service(
        database_client: AsyncSession = Depends(get_db_session),
        user_service: AuthUserService = Depends(get_user_service)
) -> OAuthService:
    service = OAuthService(database_client=database_client, user_service=user_service)
    return service
