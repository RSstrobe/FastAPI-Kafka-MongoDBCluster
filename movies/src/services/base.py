from abc import ABC, abstractmethod
import math
from typing import Type
from pydantic import BaseModel
from uuid import UUID

from elasticsearch import NotFoundError

# from db.redis import get_cache, save_cache
from models.models import FilmFull, Genre, Person, Page, Film
from repositories.elastic_repository import ElasticRepository
from repositories.redis_repository import RedisRepository


class ServiceInterface(ABC):
    @abstractmethod
    async def get_by_id(self, entity_id: UUID) -> list:
        raise NotImplementedError()


class SearchInterface(ABC):
    @abstractmethod
    async def search_by_query(
        self,
        search_query: dict,
        key_cache: str,
        page_size: int,
        page_number: int,
        index: str,
        response_model: BaseModel,
    ) -> Page | None:
        raise NotImplementedError()


class BaseService(ServiceInterface):
    """Базовый класс для получения информации о сущности по id"""

    def __init__(
        self,
        search_client: ElasticRepository,
        cache_client: RedisRepository,
        index: str,
        response_model: BaseModel,
    ):
        self.search_client = search_client
        self.cache_client = cache_client
        self.index = index
        self.response_model = response_model

    async def get_by_id(
        self, entity_id: UUID
    ) -> Type[FilmFull | Genre | Person | None]:
        key = f"{self.index}_id_{entity_id}"
        response = await self.cache_client.get(key)
        if not response:
            response = await self.search_client.get(index=self.index, id=entity_id)
            if response and "_source" in response.keys():
                response = response["_source"]
        if response:
            await self.cache_client.save(key, self.response_model(**response).json())
            return self.response_model(**response)
        return None


class BasePaginatorService(SearchInterface):
    def __init__(self, search_client: ElasticRepository, cache_client: RedisRepository):
        self.search_client = search_client
        self.cache_client = cache_client

    @staticmethod
    def get_total_pages(elastic_response: dict, page_size: int) -> int:
        total_documents = elastic_response["hits"]["total"]["value"]
        total_pages = math.ceil(total_documents / page_size)
        return total_pages

    async def search_by_query(
        self,
        search_query: dict,
        key_cache: str,
        page_size: int,
        page_number: int,
        index: str,
        response_model: Type[Genre | Person | Film],
    ) -> Page | None:
        response = await self.cache_client.get(key_cache)
        if not response:
            try:
                res = await self.search_client.search(index=index, body=search_query)

                total_pages = self.get_total_pages(res, page_size)

                response = [
                    response_model(**doc["_source"]) for doc in res["hits"]["hits"]
                ]

                response = Page(
                    response=response,
                    page=page_number,
                    page_size=page_size,
                    total_pages=total_pages,
                )
                # TODO(MosyaginGrigorii): нужно бы, по-хорошему, пересчитывать page_size
                await self.cache_client.save(key_cache, response.json())
                return response
            except NotFoundError:
                return None
        return response
