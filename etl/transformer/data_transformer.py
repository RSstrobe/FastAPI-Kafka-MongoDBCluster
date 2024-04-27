"""
Модуль для обработки сырых данных из Postgres в формат, пригодный для записи в Elasticsearch.
"""
from typing import List, Dict, Union, Type

from psycopg2.extras import RealDictRow

from transformer.index_models import Movie, Genre, Person
from common import logger, setting

transformer_logger = logger.ETLLogger()


class DataTransformer:
    """
    Класс для обработки данных.
    """

    def __init__(self, settings: setting.Settings) -> None:
        self.settings: setting = settings
        self.data_model: Type[Union[Movie, Genre, Person]] = self.get_data_model()

    def get_data_model(self) -> Type[Union[Genre, Movie]]:
        """
        Метод для получения модели данных по названию индекса.

        :return: модель данных (Movie или Genre)
        """
        if self.settings.ES_INDEX_NAME == self.settings.MOVIES_INDEX:
            model = Movie
        elif self.settings.ES_INDEX_NAME == self.settings.GENRES_INDEX:
            model = Genre
        elif self.settings.ES_INDEX_NAME == self.settings.PERSONS_INDEX:
            model = Person
        else:
            raise ValueError(f"Unknown index name: {self.settings.ES_INDEX_NAME}")

        return model

    @staticmethod
    def transform_names(
        raw_person_data: List[RealDictRow], key_name: str
    ) -> List[dict]:
        """
        Метод для обработки полей actors и writers.

        :param raw_person_data: необработанные данные о персоналиях
        :param key_name: название поля c именем

        :return: Обработанные данные о персоналиях с наличием только необходимых полей (id, name).
        """

        transformed_person_data: List[dict] = []

        if raw_person_data:
            for person_data in raw_person_data:
                transformed_person_data.append(
                    {"id": person_data["id"], key_name: person_data[key_name]}
                )

        return transformed_person_data

    def prepare_raw_genres_data(self, raw_data: List[RealDictRow]) -> List[dict]:
        """
        Метод для обработки сырых данных из Postgres.

        :param raw_data: не обработанные данные из Postgres

        :return: обработанные данные, готовые для валидации
        """

        transformer_logger.logger.info("Starting raw data batch prepare")

        prepared_data: List[dict] = []

        for row in raw_data:
            prepared_data.append(
                {
                    "id": row["id"],
                    "name": row["name"],
                    "description": row["description"] if row["description"] else "",
                }
            )

        transformer_logger.logger.info("Ending raw data batch prepare")

        return prepared_data

    def prepare_raw_movies_data(self, raw_data: List[RealDictRow]) -> List[dict]:
        """
        Метод для обработки сырых данных из Postgres.

        :param raw_data: необработанные данные из Postgres

        :return: обработанные данные, готовые для валидации
        """

        transformer_logger.logger.info("Starting raw data batch prepare")

        prepared_data: List[dict] = []

        for row in raw_data:
            actors_list: List[dict] = self.transform_names(
                row["actors"], key_name="full_name"
            )
            writers_list: List[dict] = self.transform_names(
                row["writers"], key_name="full_name"
            )
            directors_list: List[dict] = self.transform_names(
                row["director"], key_name="full_name"
            )
            genres: List[dict] = self.transform_names(row["genres"], key_name="name")

            prepared_data.append(
                {
                    "id": row["fw_id"],
                    "title": row["title"],
                    "description": row["description"] if row["description"] else "",
                    "rating": row["rating"],
                    "created": row["created"],
                    "modified": row["modified"],
                    "genres": genres,
                    "actors_names": row["actors_names"] if row["actors_names"] else [],
                    "writers_names": row["writers_names"]
                    if row["writers_names"]
                    else [],
                    "directors": directors_list,
                    "actors": actors_list,
                    "writers": writers_list,
                }
            )

        transformer_logger.logger.info("Ending raw data batch prepare")

        return prepared_data

    def prepare_raw_persons_data(self, raw_data: List[RealDictRow]) -> List[dict]:
        """
        Метод для обработки сырых данных из Postgres.

        :param raw_data: не обработанные данные из Postgres

        :return: обработанные данные, готовые для валидации
        """

        transformer_logger.logger.info("Starting raw data batch prepare")

        prepared_data: List[dict] = []

        for row in raw_data:
            prepared_data.append(
                {
                    "id": row["id"],
                    "full_name": row["full_name"],
                    "films": [
                        {"uuid": key, "roles": row["films"][key]}
                        for key in row["films"].keys()
                    ],
                }
            )

        transformer_logger.logger.info("Ending raw data batch prepare")

        return prepared_data

    def prepare_raw_data(self, raw_data: List[RealDictRow]) -> List[dict]:
        """
        Метод для обработки сырых данных из Postgres.

        :return: обработанные данные, готовые для валидации
        """
        prepared_data: List[dict] = []

        if self.settings.ES_INDEX_NAME == self.settings.MOVIES_INDEX:
            prepared_data = self.prepare_raw_movies_data(raw_data)
        elif self.settings.ES_INDEX_NAME == self.settings.GENRES_INDEX:
            prepared_data = self.prepare_raw_genres_data(raw_data)
        elif self.settings.ES_INDEX_NAME == self.settings.PERSONS_INDEX:
            prepared_data = self.prepare_raw_persons_data(raw_data)

        return prepared_data

    def validated_data(self, prepared_data: List[dict]) -> Dict[str, str]:
        """
        Метод для валидации обработанных данных.

        :param prepared_data: обработанные данные, готовые для валидации

        :return: валидированные данные, готовые для записи в elasticsearch
        """

        transformer_logger.logger.info("Starting prepared batch data validation")

        validated_data: Dict[str, str] = {}

        for data in prepared_data:
            validated_data[data["id"]] = self.data_model(**data).model_dump_json()

        transformer_logger.logger.info("Ending prepared batch data validation")

        return validated_data

    def start_transform(self, raw_data: List[RealDictRow]) -> Dict[str, str]:
        """
        Метод начала обработки данных.

        :param raw_data: необработанные данные из Postgres

        :return: Список обработанных, отвалижированных докуметов, готовых для записи в elasticsearch.
        """
        transformer_logger.logger.info("Start transform batch")

        prepared_data = self.prepare_raw_data(raw_data=raw_data)

        processed_data = self.validated_data(prepared_data=prepared_data)

        transformer_logger.logger.info("Ending transform batch")

        return processed_data
