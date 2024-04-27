from fastapi import APIRouter, Depends, status, Response, Cookie, Request, HTTPException
from fastapi.responses import RedirectResponse
from fastapi_limiter.depends import RateLimiter
from redis.asyncio import Redis

from core.config import settings
from core.constants import UserRoleEnum
from db.redis import get_redis
from helpers import access
from helpers.providers import Providers
from helpers.random import get_random_string
from schemas import histories
from schemas import users, roles, jwt_schemas
from schemas.base import Page
from services.auth_service import AuthJWT, get_auth_jwt
from services.history_service import HistoryService, get_history_service
from services.role_service import AuthRoleService, get_role_service
from services.social_service import YandexSocialService, get_yandex_service
from services.user_service import AuthUserService, get_user_service

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    path="/signup/",
    response_model=users.UserBaseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация пользователя",
    description="Регистрация пользователя по обязательным полям",
    dependencies=[Depends(RateLimiter(times=2, seconds=5))],
)
async def create_user(
    user_dto: users.CreateUserSchema = Depends(),
    user_service: AuthUserService = Depends(get_user_service),
    role_service: AuthRoleService = Depends(get_role_service),
) -> users.UserBaseSchema:
    """User registration endpoint by required fields."""

    user_encode = await user_service.create(user_dto=user_dto)
    user = users.UserBaseSchema(email=user_encode["email"])
    await role_service.set_role(
        user_role=roles.UserRoleDto(
            user_email=user_encode["email"], role_name=UserRoleEnum.DefaultUser.value
        )
    )
    return user


@router.post(
    path="/login/",
    status_code=status.HTTP_200_OK,
    summary="Авторизация пользователя",
    description="Регистрация пользователя по логину и паролю",
    dependencies=[Depends(RateLimiter(times=2, seconds=5))],
)
async def login_user(
    response: Response,
    request: Request,
    user_dto: users.LoginUserSchema = Depends(),
    user_service: AuthUserService = Depends(get_user_service),
    history_service: HistoryService = Depends(get_history_service),
    auth_service: AuthJWT = Depends(get_auth_jwt),
    redis: Redis = Depends(get_redis),
) -> dict:
    """User login endpoint by email and password."""
    user_dto = await user_service.check_user(user_dto)
    if not user_dto:
        raise HTTPException(
            detail="Incorrect email or password.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    user_agent = await history_service.create(
        user_id=user_dto.id,
        device_id=request.headers.get("User-Agent"),
    )

    action = await user_service.get_role(user_dto)

    tokens = await auth_service.create_tokens(
        data=user_dto,
        user_agent=user_agent,
        actions=action,
        redis=redis,
    )
    response.set_cookie(
        key="access_token",
        value=tokens.access_token,
        httponly=True,
        max_age=settings.auth_jwt.access_token_lifetime,
    )
    response.set_cookie(
        key="refresh_token",
        value=tokens.refresh_token,
        httponly=True,
        max_age=settings.auth_jwt.refresh_token_lifetime,
    )
    return {"detail": "login successful"}


@router.get(
    path="/login/{provider}",
    summary="Аунтификация через соц. сети",
    description="Аунтификация по протоколу OAuth2 через социальные сети",
    dependencies=[Depends(RateLimiter(times=2, seconds=5))],
)
async def login_oauth(
    provider: Providers,
    request: Request,
):
    redirect_uri = request.url_for("login_oauth_callback", provider=provider.value)
    state = get_random_string(16)
    request.session["state"] = state

    if provider == Providers.YANDEX:
        resopnse = RedirectResponse(
            f"https://oauth.yandex.ru/authorize"
            f"?response_type=code"
            f"&client_id={settings.yandex.client_id}"
            f"&redirect_uri={redirect_uri}"
            f"&state={state}",
        )

        return resopnse


@router.get(
    path="/login/{provider}/callback",
    dependencies=[Depends(RateLimiter(times=2, seconds=5))],
)
async def login_oauth_callback(
    code: str,
    state: str,
    request: Request,
    provider: Providers,
    yandex_service: YandexSocialService = Depends(get_yandex_service),
    user_service: AuthUserService = Depends(get_user_service),
    history_service: HistoryService = Depends(get_history_service),
    auth_service: AuthJWT = Depends(get_auth_jwt),
    redis: Redis = Depends(get_redis),
) -> RedirectResponse:
    if state != request.session["state"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="State check is failed",
        )

    user = None
    if provider == Providers.YANDEX:
        user = await yandex_service.get_user(code)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    redirect = RedirectResponse(url="http://0.0.0.0/auth/api/openapi")
    try:
        user_dto = await user_service.get(email=user.email)
    except AttributeError:
        user_dto = await user_service.get(email=user["email"])

    user_agent = await history_service.create(
        user_id=user_dto.id,
        device_id=request.headers.get("User-Agent"),
    )

    action = await user_service.get_role(user_dto)

    tokens = await auth_service.create_tokens(
        data=user_dto,
        user_agent=user_agent,
        actions=action,
        redis=redis,
    )
    redirect.set_cookie(
        key="access_token",
        value=tokens.access_token,
        httponly=True,
        max_age=settings.auth_jwt.access_token_lifetime,
    )
    redirect.set_cookie(
        key="refresh_token",
        value=tokens.refresh_token,
        httponly=True,
        max_age=settings.auth_jwt.refresh_token_lifetime,
    )
    return redirect


@router.put(
    path="/change_password/",
    status_code=status.HTTP_200_OK,
    summary="Изменение пароля",
    description="Изменить пароль по access token",
    dependencies=[Depends(RateLimiter(times=2, seconds=5))],
)
@access.check_access_token  # Декоратор для проверки прав пользователя
async def change_password(
    access_token: str | None = Cookie(None),
    user_service: AuthUserService = Depends(get_user_service),
    auth_service: AuthJWT = Depends(get_auth_jwt),
    password_data: users.ChangePasswordSchema = Depends(),
) -> dict:
    """Change password by access token."""
    user_info = await auth_service.decode_jwt(access_token)
    await user_service.update(user_info["sub"], password_data)
    return {"detail": "Successfully changed password."}


@router.get(
    path="/refresh/",
    summary="Обновления refresh token",
    description="Получение новых access token и refresh token",
    dependencies=[Depends(RateLimiter(times=2, seconds=5))],
)
async def refresh(
    response: Response,
    refresh_token: str = Cookie(None),
    user_service: AuthUserService = Depends(get_user_service),
    auth_service: AuthJWT = Depends(get_auth_jwt),
    redis: Redis = Depends(get_redis),
) -> dict:
    """Get new access and refresh tokens."""
    if not await auth_service.check_refresh_token(
        refresh_token,
        redis,
    ):
        raise HTTPException(
            detail="Incorrect token.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    user_info = await auth_service.decode_jwt(refresh_token)
    user_info = jwt_schemas.RefreshJWTSchema(**user_info)
    action = await user_service.get_role(user_info)

    user_agent = user_info.client_id

    _new_tokens = await auth_service.create_tokens(
        data=user_info,
        user_agent=user_agent,
        actions=action,
        redis=redis,
    )
    await auth_service.delete_refresh_token(refresh_token, redis)
    response.set_cookie(
        key="access_token",
        value=_new_tokens.access_token,
        httponly=True,
        max_age=settings.auth_jwt.access_token_lifetime,
    )
    response.set_cookie(
        key="refresh_token",
        value=_new_tokens.refresh_token,
        httponly=True,
        max_age=settings.auth_jwt.refresh_token_lifetime,
    )
    return {"detail": "Successfully refresh"}


@router.post(
    path="/logout/",
    summary="Выход из профиля",
    description="Выход из профиля по refresh token",
    dependencies=[Depends(RateLimiter(times=2, seconds=5))],
)
async def logout(
    response: Response,
    refresh_token: str | None = Cookie(None),
    auth_service: AuthJWT = Depends(get_auth_jwt),
    history_service: HistoryService = Depends(get_history_service),
    redis: Redis = Depends(get_redis),
) -> dict:
    """Logout endpoint by access token."""
    user_info = await auth_service.decode_jwt(refresh_token)
    delite = await auth_service.delete_refresh_token(refresh_token, redis)
    if not delite:
        raise HTTPException(
            detail="Incorrect command.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    await history_service.update(user_info["client_id"])
    return {"detail": "logout is successfully"}


@router.get(
    path="/history/",
    response_model=Page[histories.FullHistorySchema],
    summary="Получение пользовательской истории",
    description="Получение истории пользователя по access token",
    dependencies=[Depends(RateLimiter(times=2, seconds=5))],
)
@access.check_access_token  # Декоратор для проверки прав пользователя
async def history(
    access_token: str = Cookie(None),
    auth_service: AuthJWT = Depends(get_auth_jwt),
    history_service: HistoryService = Depends(get_history_service),
    history_data: histories.HistoryRequestSchema = Depends(),
) -> list[histories.FullHistorySchema]:
    """Get user history by access token."""
    user_info = await auth_service.decode_jwt(access_token)
    list_history = await history_service.get(user_info["sub"], history_data)
    return list_history
