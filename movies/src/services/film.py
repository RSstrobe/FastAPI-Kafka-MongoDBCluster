from functools import lru_cache
from uuid import UUID

from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from models.models import FilmFull, Film, Page
from services.utils.search_creator import SearchBodyCreator
from services.base import BaseService, BasePaginatorService
from services.utils.search_templates import SearchTemplates
from repositories.elastic_repository import ElasticRepository
from repositories.redis_repository import RedisRepository


class FilmService(BaseService, BasePaginatorService, SearchBodyCreator):
    def __init__(self, search_client: ElasticRepository, cache_client: RedisRepository):
        super().__init__(
            search_client=search_client,
            cache_client=cache_client,
            index="movies",
            response_model=FilmFull,
        )

    async def get_list_films_by_similar_genre(
        self, film_id: UUID, page_size: int, page_number: int
    ) -> Page[Film] | None:
        key_cache = f"film_id_genres_{film_id}"

        # TODO(MosyaginGrigorii): Надо бы в один запрос, если это возможно
        film_full_data = await self.get_by_id(entity_id=film_id)
        genres_ids = [row.id for row in film_full_data.genres]

        search_query = self.create_search_body(
            search_template=SearchTemplates.films_by_genre_ids(genre_ids=genres_ids),
            sort_query="-imdb_rating",
            page_size=page_size,
            page_number=page_number,
        )

        res = await self.search_by_query(
            search_query=search_query,
            key_cache=key_cache,
            page_size=page_size,
            page_number=page_number,
            index=self.index,
            response_model=self.response_model,
        )
        return res

    async def get_list_films_main_page(
        self, sort: str, page_size: int, page_number: int, filter_query: UUID
    ) -> Page[Film] | None:
        key_cache = f"films_{sort}_{page_size}_{page_number}_{filter_query}"
        genres_ids = [] if filter_query is None else [filter_query]

        search_query = self.create_search_body(
            search_template=SearchTemplates.films_by_genre_ids(genre_ids=genres_ids),
            sort_query="-imdb_rating",
            page_size=page_size,
            page_number=page_number,
        )

        res = await self.search_by_query(
            search_query=search_query,
            key_cache=key_cache,
            page_size=page_size,
            page_number=page_number,
            index=self.index,
            response_model=self.response_model,
        )
        return res

    async def search_films_by_query(
        self, query: str, page_size: int, page_number: int
    ) -> Page[Film] | None:
        key_cache = f"films_{query}_{page_size}_{page_number}"

        search_query = self.create_search_body(
            search_template=SearchTemplates.films_search_template(search_query=query),
            sort_query="-imdb_rating",
            page_size=page_size,
            page_number=page_number,
        )

        res = await self.search_by_query(
            search_query=search_query,
            key_cache=key_cache,
            page_size=page_size,
            page_number=page_number,
            index=self.index,
            response_model=self.response_model,
        )
        return res


@lru_cache()
def get_film_service(
    elastic: ElasticRepository = Depends(get_elastic),
    redis: RedisRepository = Depends(get_redis),
) -> Film | FilmService:
    return FilmService(elastic, redis)
