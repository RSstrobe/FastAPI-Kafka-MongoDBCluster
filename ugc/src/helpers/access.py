import functools
from typing import Callable
from datetime import datetime

import jwt
from flask import request

from core.config import settings
from core.exceptions import TokenException, ForbiddenException


async def is_token_expired(token: str, action_name: str) -> dict:
    if not token:
        raise TokenException
    token_info: dict = jwt.decode(
        jwt=token,
        key=settings.auth_jwt.public_key.read_text(),
        algorithms=[
            settings.auth_jwt.auth_algorithm_password,
        ],
    )

    token_expired = datetime.utcfromtimestamp(token_info.get("exp"))
    if token_expired < datetime.utcnow():
        raise TokenException

    user_actions = token_info.get("actions")
    if action_name not in user_actions:
        raise ForbiddenException
    return token_info


def check_access_token(func: Callable):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        user_info = request.cookies.to_dict()
        access_token = user_info.get("access_token")
        token_info = await is_token_expired(access_token, action_name=func.__name__)
        kwargs["user_info"] = token_info
        return await func(*args, **kwargs)

    return wrapper
