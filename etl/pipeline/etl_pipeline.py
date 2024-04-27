"""
Модуль для старта расчета ETL процесса.
"""
from typing import Optional

from extractor.data_extractor import DataExtractor
from transformer.data_transformer import DataTransformer
from loader.data_loader import DataLoader
from state.etl_state import JsonFileStorage, State
from common import setting, logger

etl_logger = logger.ETLLogger()


class ETL:
    """
    Класс ETL процесса.
    """

    def __init__(self) -> None:
        self.settings: setting = setting.Settings()
        self.storage: Optional[JsonFileStorage] = None
        self.state: Optional[State] = None
        self.data_extractor: Optional[DataExtractor] = None
        self.data_transformer: Optional[DataTransformer] = None
        self.data_loader: Optional[DataLoader] = None

    def redefine_settings(self, index_name: str) -> None:
        """
        Метод для переопределения настроек ETL процесса.

        :param index_name: Имя индекса для Elasticsearch.
        """
        self.settings.ES_INDEX_NAME = index_name
        self.settings.PATH_STATE_JSON = self.settings.PATH_STATE_JSON.format(
            index_name=index_name
        )
        self.settings.PATH_MOVIES_INDEX_JSON = (
            self.settings.PATH_MOVIES_INDEX_JSON.format(index_name=index_name)
        )

    def setup_etl(self, index_name: str) -> None:
        """
        Метод для настроек ETL процесса.

        :param index_name: Имя индекса для Elasticsearch.
        """
        self.redefine_settings(index_name=index_name)
        self.storage: JsonFileStorage = JsonFileStorage(
            file_path=self.settings.PATH_STATE_JSON
        )
        self.state: State = State(storage=self.storage)
        self.data_extractor: DataExtractor = DataExtractor(
            state=self.state, settings=self.settings
        )
        self.data_transformer: DataTransformer = DataTransformer(settings=self.settings)
        self.data_loader: DataLoader = DataLoader(settings=self.settings)

    def start_etl(self, index_name: str) -> None:
        """
        Метод для запуска ETL процесса.

        :param index_name: Имя индекса для Elasticsearch.
        """
        etl_logger.logger.info("Start ETL process")

        self.setup_etl(index_name=index_name)

        raw_data = self.data_extractor.start_reader()

        for batch_raw_data in raw_data:
            if batch_raw_data:
                transformed_data = self.data_transformer.start_transform(
                    raw_data=batch_raw_data
                )
                self.data_loader.start_load(data=transformed_data)
                self.state.create_state(data=transformed_data)
            else:
                etl_logger.logger.info("No data to load")

        etl_logger.logger.info("ETL process finished")
