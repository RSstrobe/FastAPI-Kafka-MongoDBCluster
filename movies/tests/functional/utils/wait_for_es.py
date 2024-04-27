from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError

from subsidiary.backoff import backoff
from tests.functional.core.settings import test_settings


@backoff(connect_exception=ConnectionError)
def pinging_elastic(elastic_client: Elasticsearch):
    """Waiting for test Elasticsearch service response"""
    return elastic_client.ping()


if __name__ == "__main__":
    client = Elasticsearch(
        hosts=[f"{test_settings.elastic_host}:{test_settings.elastic_port}"]
    )
    pinging_elastic(elastic_client=client)
