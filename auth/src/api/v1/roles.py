from fastapi import APIRouter, Depends, status, Path, Response, Cookie
from fastapi_limiter.depends import RateLimiter

from helpers import access
from helpers.exceptions import AuthRoleNotVerifyException
from schemas import roles
from services.role_service import AuthRoleService, get_role_service

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/roles/create",
    status_code=status.HTTP_201_CREATED,
    description="Создать роль на основании имеющихся возможных действий",
    summary="Создать роль",
    dependencies=[Depends(RateLimiter(times=2, seconds=5))],
)
@access.check_access_token  # Декоратор для проверки прав пользователя
async def create_role(
    access_token: str | None = Cookie(None),
    role_dto: roles.RoleActionDto = Depends(),
    role_service: AuthRoleService = Depends(get_role_service),
):
    response = await role_service.create(role_dto)
    return response


@router.get(
    path="/roles/read",
    response_model=list[roles.RoleActionSchema],
    status_code=status.HTTP_200_OK,
    description="Получить существующие роли с детализацией по разрешенным действиям",
    summary="Получить существующие роли",
    dependencies=[Depends(RateLimiter(times=2, seconds=5))],
)
@access.check_access_token  # Декоратор для проверки прав пользователя
async def get_roles(
    access_token: str | None = Cookie(None),
    role_service: AuthRoleService = Depends(get_role_service),
) -> list[roles.RoleActionSchema]:
    response = await role_service.get()
    return response


@router.put(
    "/roles/update",
    status_code=status.HTTP_200_OK,
    description="Изменить название, комментарий и разрешенные действия у существующей роли",
    summary="Изменить существующую роль",
    dependencies=[Depends(RateLimiter(times=2, seconds=5))],
)
@access.check_access_token  # Декоратор для проверки прав пользователя
async def change_role(
    access_token: str | None = Cookie(None),
    role_dto: roles.RoleActionDto = Depends(),
    role_service: AuthRoleService = Depends(get_role_service),
):
    response = await role_service.update(role_dto)
    return response


@router.delete(
    "/roles/delete/{name}",
    status_code=status.HTTP_200_OK,
    description="Изменить название, комментарий и разрешенные действия у существующей роли",
    summary="Изменить существующую роль",
)
@access.check_access_token  # Декоратор для проверки прав пользователя
async def delete_role(
    access_token: str | None = Cookie(None),
    name: str = Path(max_length=50, title="Имя роли"),
    role_service: AuthRoleService = Depends(get_role_service),
) -> Response:
    await role_service.delete(name=name)
    return Response(status_code=status.HTTP_200_OK)


@router.post(
    "/roles/set",
    status_code=status.HTTP_201_CREATED,
    description="Назначить роль пользователю",
    summary="Назначить роль пользователю",
)
@access.check_access_token  # Декоратор для проверки прав пользователя
async def set_role(
    access_token: str | None = Cookie(None),
    user_dto: roles.UserRoleDto = Depends(),
    role_service: AuthRoleService = Depends(get_role_service),
):
    await role_service.set_role(user_role=user_dto)
    return Response(status_code=status.HTTP_201_CREATED)


@router.post(
    "/roles/verify",
    status_code=status.HTTP_200_OK,
    description="Верифицировать роль пользователя",
    summary="Верифицировать роль пользователя",
)
@access.check_access_token  # Декоратор для проверки прав пользователя
async def verify_role(
    access_token: str | None = Cookie(None),
    user_dto: roles.UserRoleDto = Depends(),
    role_service: AuthRoleService = Depends(get_role_service),
) -> Response:
    response = await role_service.verify(user_role=user_dto)
    if not response:
        raise AuthRoleNotVerifyException()
    return Response(status_code=status.HTTP_200_OK)
