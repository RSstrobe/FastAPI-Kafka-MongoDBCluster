from uuid import UUID
from .base import BaseSchema


class JWTSchema(BaseSchema):
    iat: int
    exp: int
    client_id: str
    jti: str


class AccessJWTSchema(JWTSchema):
    sub: UUID
    actions: list[str]


class RefreshJWTSchema(JWTSchema):
    id: str


class ResponseTokenSchema(JWTSchema):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
