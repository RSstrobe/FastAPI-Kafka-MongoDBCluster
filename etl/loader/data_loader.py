"""
Модуль для записи обработанных данных в Elasticsearch.
"""
import json
from typing import Dict, Iterator, Type
from contextlib import closing

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from common import setting, logger, backoff

loader_logger = logger.ETLLogger()


class DataLoader:
    """
    Класс для загрузки данных в Elasticsearch.
    """

    def __init__(self, settings: setting.Settings) -> None:
        self.client: Type[Elasticsearch] = Elasticsearch
        self.settings: setting = settings
        self.index_name: str = self.settings.ES_INDEX_NAME
        self.es_host: str = self.settings.ELASTICSEARCH_HOST
        self.index_mapping: dict = {}

    def is_index_exists(self) -> None:
        """
        Метод для проверки существования индекса.

        Если индекс не существует - создается индекс.
        """
        loader_logger.logger.info("Check index exists %s", self.index_name)

        is_index_exists = self.client.indices.exists(index=self.index_name)

        if not is_index_exists:
            loader_logger.logger.info("Index %s not exists", self.index_name)
            self.create_index()
        else:
            loader_logger.logger.info("Index %s exists", self.index_name)

    def load_index_mapping(self) -> None:
        """
        Метод для загрузки маппинга индекса.
        """
        loader_logger.logger.info("Load index mapping %s", self.index_name)

        with open(self.settings.PATH_MOVIES_INDEX_JSON, "r") as fp:
            self.index_mapping = json.load(fp)

        loader_logger.logger.info("Index mapping %s loaded", self.index_name)

    def create_index(self) -> None:
        """
        Метод для создания индекса.
        """
        loader_logger.logger.info("Creating index %s", self.index_name)

        self.load_index_mapping()
        self.client.indices.create(index=self.index_name, body=self.index_mapping)

        loader_logger.logger.info("Index %s created", self.index_name)

    def doc_generator(self, data: Dict[str, str]) -> Iterator[Dict[str, str]]:
        """
        Метод для генерации документов для Elasticsearch.

        :param data: данные для записи в Elasticsearch.

        :yield: данные, готовые для записи в Elasticsearch c помощью bulk/update.
        """
        for source_id, source in data.items():
            yield {
                "op_type": "update",
                "_index": self.index_name,
                "_id": source_id,
                "_source": source,
            }

    def write_documents(self, data: Dict[str, str]) -> None:
        """
        Метод для записи данных в Elasticsearch.

        :param data: данные для записи в Elasticsearch
        """
        loader_logger.logger.info("Start write batch data")

        bulk(
            client=self.client,
            actions=self.doc_generator(data),
            index=self.index_name,
            chunk_size=self.settings.BATCH_SIZE_ES,
        )

        loader_logger.logger.info("End write batch data")

    @backoff.etl_backoff
    def start_load(self, data: Dict[str, str]) -> None:
        """
        Метод начала записи данных в Elasticsearch.
        """

        loader_logger.logger.info("Start load batch data")

        with closing(Elasticsearch(self.es_host)) as self.client:
            self.is_index_exists()

            self.write_documents(data=data)

        loader_logger.logger.info("End load batch data")
