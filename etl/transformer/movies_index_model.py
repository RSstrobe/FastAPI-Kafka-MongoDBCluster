"""
Модуль для определения модели данных индекса movies.
"""
from typing import List, Dict, Optional, Any, Union
from uuid import UUID

from pydantic import BaseModel, Field


class Movie(BaseModel):
    id: UUID = Field(alias="fw_id", description="UUID произведения (фильм/сериал)")
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
