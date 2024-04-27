from typing import TypeVar, Generic

import orjson
from pydantic import BaseModel

T = TypeVar("T")


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class BaseSchema(BaseModel):
    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class Page(BaseModel, Generic[T]):
    response: list[T]
    page: int
    page_size: int
    total_pages: int
