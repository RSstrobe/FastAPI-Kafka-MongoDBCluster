import uuid
from datetime import datetime, timedelta
from typing import Any

import jwt
from fastapi import status
from fastapi.exceptions import HTTPException
from redis import Redis
from redis.exceptions import ConnectionError, DataError

from core.config import settings
from schemas.users import LoginUserResponseSchema


class AuthJWT:
    def __init__(self, algorithm: str, private_key: str, public_key: str):
        self.algorithm: str = algorithm
        self.private_key: str = private_key
        self.public_key: str = public_key

    async def encode_jwt(
        self,
        payload: dict[str, Any],
    ) -> str:
        encoded = jwt.encode(payload, self.private_key, self.algorithm)
        return encoded

    async def decode_jwt(
        self,
        jwt_token: str | bytes,
    ):
        decoded = jwt.decode(jwt_token, self.public_key, algorithms=[self.algorithm])
        return decoded

    async def create_token(self, data: dict, token_timelife: int):
        """Base function for creating a new jwt tokens."""
        to_encode = data.copy()
        iatime = datetime.utcnow()
        expire = iatime + timedelta(seconds=token_timelife)
        to_encode.update(
            {
                "iat": iatime,
                "exp": expire,
                "jti": str(uuid.uuid4()),
            }
        )
        return await self.encode_jwt(to_encode)

    async def create_access_token(self, data: dict, actions: str):
        access_token_data = {
            "sub": str(data["id"]),
            "actions": actions,
            "client_id": str(data["client_id"]),
        }
        access_token = await self.create_token(
            data=access_token_data,
            token_timelife=settings.auth_jwt.access_token_lifetime,
        )
        return access_token

    async def create_refresh_token(self, data: dict, redis: Redis):
        refresh_token_data = {
            "id": str(data["id"]),
            "client_id": str(data["client_id"]),
        }
        refresh_token = await self.create_token(
            data=refresh_token_data,
            token_timelife=settings.auth_jwt.refresh_token_lifetime,
        )
        try:
            await redis.sadd("refresh_tokens", refresh_token)
        except ConnectionError:
            raise HTTPException(
                detail="Service unavailable.",
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        return refresh_token

    async def create_tokens(self, data, user_agent: str, actions: str, redis: Redis):
        data = {"id": data.id, "client_id": user_agent}
        _access_token = await self.create_access_token(
            data=data,
            actions=actions,
        )
        _refresh_token = await self.create_refresh_token(
            data=data,
            redis=redis,
        )
        return LoginUserResponseSchema(
            access_token=_access_token,
            refresh_token=_refresh_token,
        )

    @staticmethod
    async def delete_refresh_token(refresh_token: str, redis: Redis) -> bool:
        try:
            await redis.srem("refresh_tokens", refresh_token)
            return True
        except DataError:
            return False

    @staticmethod
    async def check_refresh_token(refresh_token: str, redis: Redis) -> bool:
        refresh_tokens = [
            refresh_token.decode("UTF-8")
            for refresh_token in await redis.smembers("refresh_tokens")
        ]
        return refresh_token in refresh_tokens


def get_auth_jwt():
    auth_jwt = AuthJWT(
        algorithm=settings.auth_jwt.auth_algorithm_password,
        private_key=settings.auth_jwt.private_key.read_text(),
        public_key=settings.auth_jwt.public_key.read_text(),
    )
    return auth_jwt
