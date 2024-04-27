from functools import lru_cache
from uuid import UUID

from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from models.models import Person, Page, Film
from services.utils.search_creator import SearchBodyCreator
from services.base import BaseService, BasePaginatorService
from services.utils.search_templates import SearchTemplates
from repositories.elastic_repository import ElasticRepository
from repositories.redis_repository import RedisRepository


class PersonService(BaseService, BasePaginatorService, SearchBodyCreator):
    """
    Класс для работы с endpoint'ами, относящимися к бизнес-логике genre
    """

    def __init__(self, search_client: ElasticRepository, cache_client: RedisRepository):
        super().__init__(
            search_client=search_client,
            cache_client=cache_client,
            index="persons",
            response_model=Person,
        )

    async def search_persons_by_query(
        self, query: str, page_size: int, page_number: int
    ) -> Page[Person] | None:
        key_cache = f"persons_{query}_{page_size}_{page_number}"

        search_query = self.create_search_body(
            search_template=SearchTemplates.persons_search_template(search_query=query),
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

    # TODO(MosyaginGrigorii): Тут можно сделать пагинацию
    async def get_list_films_by_person(
        self, person_id: UUID, page_size: int, page_number: int
    ) -> Page[Film] | None:
        key_cache = f"person_films_{person_id}_{page_size}_{page_number}"

        search_query = self.create_search_body(
            search_template=SearchTemplates.search_films_by_person_id(
                person_id=person_id
            ),
            sort_query="-imdb_rating",
            page_size=page_size,
            page_number=page_number,
        )

        res = await self.search_by_query(
            search_query=search_query,
            key_cache=key_cache,
            page_size=page_size,
            page_number=page_number,
            index="movies",
            response_model=Film,
        )
        return res


@lru_cache()
def get_person_service(
    elastic: ElasticRepository = Depends(get_elastic),
    redis: RedisRepository = Depends(get_redis),
) -> PersonService:
    return PersonService(elastic, redis)
