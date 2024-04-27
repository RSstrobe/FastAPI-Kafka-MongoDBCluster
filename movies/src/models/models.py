import orjson
from pydantic import BaseModel
from uuid import UUID
from typing import Generic, TypeVar

ROLES = ["actor", "writer", "director"]
T = TypeVar("T")


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class BaseModelAPI(BaseModel):
    id: UUID

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class Page(BaseModel, Generic[T]):
    response: list[T]
    page: int
    page_size: int
    total_pages: int

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class Film(BaseModelAPI):
    imdb_rating: float | None
    title: str


class Genre(BaseModelAPI):
    name: str


class FilmPerson(BaseModelAPI):
    full_name: str


class PersonFilm(BaseModelAPI):
    roles: list[str]


class Person(BaseModelAPI):
    full_name: str
    films: list[PersonFilm]


class FilmFull(Film):
    description: str
    genres: list[Genre]
    actors: list[FilmPerson]
    writers: list[FilmPerson]
    directors: list[FilmPerson]
