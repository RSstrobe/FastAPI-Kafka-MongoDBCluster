"""
Модуль для определения модели данных индекса movies.
"""
from typing import List, Dict, Optional, Any, Union
from uuid import UUID

from pydantic import BaseModel, Field


class Movie(BaseModel):
    id: UUID = Field(alias="id", description="UUID произведения (фильм/сериал)")
    imdb_rating: Optional[float] = Field(
        alias="rating", description="Рейтинг произведения"
    )
    genres: List[Dict] = Field(alias="genres", description="Имена жанров c id")
    title: str = Field(alias="title", description="Наименование произведения")
    description: str = Field(alias="description", description="Описание произведения")

    directors: List[Dict] = Field(alias="directors", description="Режиссер")
    actors_names: Union[List[Any], List[str]] = Field(
        alias="actors_names", description="Имена актеров"
    )
    writers_names: Union[List[Any], List[str]] = Field(
        alias="writers_names", description="Имена сценаристов"
    )

    actors: List[Dict] = Field(alias="actors", description="Имена актеров c id")
    writers: List[Dict] = Field(alias="writers", description="Имена сценаристов c id")


class Genre(BaseModel):
    id: UUID = Field(alias="id", description="UUID жанра")
    name: str = Field(alias="name", description="Наименование жанра")
    description: str = Field(alias="description", description="Описание жанра")


class FilmPerson(BaseModel):
    id: UUID = Field(alias="uuid", description="UUID произведения")
    roles: List[str] = Field(alias="roles", description="Роль персоны в произведении")


class Person(BaseModel):
    id: UUID = Field(alias="id", description="UUID персоны")
    full_name: str = Field(alias="full_name", description="Имя персоны")
    films: List[FilmPerson] = Field(alias="films", description="Роль в произведении")
