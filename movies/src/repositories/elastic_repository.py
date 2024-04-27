from uuid import UUID

from elasticsearch import Elasticsearch

from .base_repository import MixinSearchingRepository


class ElasticRepository(MixinSearchingRepository):
    elastic = Elasticsearch | None

    def __init__(self, connection=Elasticsearch):
        super().__init__(connection)

    async def get(self, index: str, id: UUID):
        response = await self.connection.get(index=index, id=id)
        return response

    async def search(self, index: str, body: dict):
        response = await self.connection.search(index=index, body=body)
        return response
