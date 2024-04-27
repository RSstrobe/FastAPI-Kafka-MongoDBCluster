import functools
from typing import Callable
from datetime import datetime

import jwt
from fastapi import HTTPException, status

from core.config import settings


async def is_token_expired(token: str, action_name: str) -> bool:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect access token.',
        )
    token_info: dict = jwt.decode(
        jwt=token,
        key=settings.auth_jwt.public_key.read_text(),
        algorithms=[settings.auth_jwt.auth_algorithm_password, ]
    )

    token_expired = datetime.utcfromtimestamp(token_info.get("exp"))
    if token_expired < datetime.utcnow():
        raise HTTPException(
            detail='Incorrect access token.',
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    user_actions = token_info.get('actions')
    if action_name not in user_actions:
        raise HTTPException(
            detail='Insufficient rights to use this function.',
            status_code=status.HTTP_403_FORBIDDEN,
        )
    return True


def check_access_token(func: Callable):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        access_token = kwargs.get('access_token')
        await is_token_expired(access_token, action_name=func.__name__)
        return await func(*args, **kwargs)

    return wrapper
