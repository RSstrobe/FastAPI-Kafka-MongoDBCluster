from uuid import UUID

from pydantic import BaseModel, Field

from core.config import settings


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


class MainPageFilter(BaseModelPaginationFilter):
    sort: str = Field(default="imdb_rating", description="Поле для сортировки")
    genre: UUID = Field(default=None, description="Жанр")


class SearchByFilm(BaseModelPaginationFilter):
    query: str = Field(min_length=1, max_length=100, description="Поисковая строка")


class SearchByPerson(BaseModelPaginationFilter):
    query: str = Field(min_length=1, max_length=100, description="Поисковая строка")
