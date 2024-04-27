from functools import lru_cache

from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from models.models import Genre, Page
from services.base import BaseService, BasePaginatorService
from services.utils.search_creator import SearchBodyCreator
from services.utils.search_templates import SearchTemplates
from repositories.elastic_repository import ElasticRepository
from repositories.redis_repository import RedisRepository


class GenreService(BaseService, BasePaginatorService, SearchBodyCreator):
    """
    Класс для работы с endpoint'ами, относящимися к бизнес-логике genre
    """

    def __init__(self, search_client: ElasticRepository, cache_client: RedisRepository):
        super().__init__(
            search_client=search_client,
            cache_client=cache_client,
            index="genres",
            response_model=Genre,
        )

    async def get_list_genres(
        self, page_size: int, page_number: int
    ) -> Page[Genre] | None:
        key_cache = f"genres_{page_size}_{page_number}"

        search_query = self.create_search_body(
            search_template=SearchTemplates.genre_templates(),
            sort_query="-id",
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
def get_genre_service(
    elastic: ElasticRepository = Depends(get_elastic),
    redis: RedisRepository = Depends(get_redis),
) -> GenreService:
    return GenreService(elastic, redis)
