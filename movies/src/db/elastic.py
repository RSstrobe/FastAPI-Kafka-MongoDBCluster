from elasticsearch import AsyncElasticsearch

from core.config import settings
from repositories.elastic_repository import ElasticRepository

es: ElasticRepository | None


async def get_elastic() -> ElasticRepository:
    elasticsearch_url = "{ES_HOST}:{ES_PORT}".format(
        ES_HOST=settings.elastic.elastic_host,
        ES_PORT=settings.elastic.elastic_port,
    )
    client = AsyncElasticsearch(elasticsearch_url)
    return ElasticRepository(connection=client)
