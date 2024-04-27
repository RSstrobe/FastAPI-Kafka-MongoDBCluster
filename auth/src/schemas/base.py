from typing import Generic, TypeVar

import orjson
from pydantic import BaseModel, Field

from core.config import settings

T = TypeVar("T")


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class BaseSchema(BaseModel):
    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
        strict = True


class BaseModelPaginationFilter(BaseModel):
    page_size: int = Field(
        default=settings.pagination.page_size,
        ge=1,
        lt=settings.pagination.max_page,
        description="Количество произведений на странице",
    )
    page_number: int = Field(
        default=1, ge=1, lt=settings.pagination.max_page, description="Номер страницы"
    )


class Page(BaseSchema, Generic[T]):
    response: list[T]
    page: int
    page_size: int
    total_pages: int

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
