from abc import ABC, abstractmethod
from functools import lru_cache

from httpx import HTTPError, AsyncClient as AsyncHTTPClient
from fastapi import status, HTTPException, Depends

from core.config import settings
from deps.http import get_async_http_client
from helpers.providers import Providers
from .oauth_service import OAuthService, get_oauth_service


class BaseSocialService(ABC):
    def __init__(
        self,
        social_name: str,
        oauth_service: OAuthService,
        http_client: AsyncHTTPClient,
    ):
        self.social_name = social_name
        self.oauth_service = (oauth_service,)
        self.http_client = http_client

    @abstractmethod
    async def get_user(self, code: str):
        raise NotImplementedError


class YandexSocialService(BaseSocialService):
    def __init__(self, oauth_service: OAuthService, http_client: AsyncHTTPClient):
        super().__init__(
            Providers.YANDEX.value, oauth_service=oauth_service, http_client=http_client
        )

    async def get_user(self, code):
        try:
            response = await self.http_client.post(
                "https://oauth.yandex.ru/token",
                data={
                    "code": code,
                    "grant_type": "authorization_code",
                    "client_id": settings.yandex.client_id,
                    "client_secret": settings.yandex.client_secret,
                },
            )
            if response.status_code != status.HTTP_200_OK:
                return HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found",
                )

            data = response.json()
            access_token = data["access_token"]
            user_info = await self.http_client.get(
                url="https://login.yandex.ru/info",
                headers={"Authorization": f"OAuth {access_token}"},
            )

            if user_info.status_code != status.HTTP_200_OK:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User information not available",
                )
            user_data = user_info.json()

        except HTTPError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Social service is not available",
            )

        return await self.oauth_service[0].get_user(
            social_id=user_data.get("psuid"),
            social_name=Providers.YANDEX.value,
            email=user_data.get("default_email"),
            name=user_data.get("real_name", ""),
        )


@lru_cache
def get_yandex_service(
    oauth_service: OAuthService = Depends(get_oauth_service),
    http_client: AsyncHTTPClient = Depends(get_async_http_client),
) -> YandexSocialService:
    return YandexSocialService(oauth_service=oauth_service, http_client=http_client)
