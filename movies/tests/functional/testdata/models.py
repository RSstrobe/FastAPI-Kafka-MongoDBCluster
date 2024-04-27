"""A module with pydantic schemas for es documents."""

from pydantic import BaseModel, Field
from typing import Optional, Any
from uuid import UUID


class Movie(BaseModel):
    id: UUID = Field(alias="id", description="UUID произведения (фильм/сериал)")
    imdb_rating: Optional[float] = Field(
        alias="imdb_rating", description="Рейтинг произведения"
    )
    genres: list[dict] = Field(alias="genre", description="Имена жанров c id")
    title: str = Field(alias="title", description="Наименование произведения")
    description: str = Field(alias="description", description="Описание произведения")

    directors: list[dict] = Field(alias="director", description="Режиссер")
    actors_names: list[Any] | list[str] = Field(
        alias="actors_names", description="Имена актеров"
    )
    writers_names: list[Any] | list[str] = Field(
        alias="writers_names", description="Имена сценаристов"
    )

    actors: list[dict] = Field(alias="actors", description="Имена актеров c id")
    writers: list[dict] = Field(alias="writers", description="Имена сценаристов c id")


class Genre(BaseModel):
    id: UUID = Field(alias="id", description="UUID жанра")
    name: str = Field(alias="name", description="Наименование жанра")
    description: str = Field(alias="description", description="Описание жанра")


class FilmPerson(BaseModel):
    id: UUID = Field(alias="id", description="UUID произведения")
    roles: list[str] = Field(alias="roles", description="Роль персоны в произведении")


class Person(BaseModel):
    id: UUID = Field(alias="id", description="UUID персоны")
    full_name: str = Field(alias="full_name", description="Имя персоны")
    films: list[FilmPerson] = Field(alias="films", description="Роль в произведении")
