"""
Модуль для хранения настроек.
"""

import os
import datetime

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """
    Класс для хранения настроек.
    """

    APP_NAME: str = Field(alias="etl_app_name", description="Имя приложения")

    DB_NAME: str = Field(alias="db_name", description="Имя БД Postgres")
    DB_USER: str = Field(alias="db_user", description="Пользователь БД Postgres")
    DB_PASSWORD: str = Field(
        alias="db_password", description="Пароль пользователя БД Postgres"
    )
    DB_HOST: str = Field(alias="db_host", description="Хост БД Postgres")
    PORT: str = Field(default="5432", alias="port", description="Порт БД Postgres")

    # Для ограничения количества строк при
    BATCH_SIZE_PG: int = 500
    BATCH_SIZE_ES: int = 100

    # Путь к файлу с данными маппинга индекса
    PATH_MOVIES_INDEX_JSON: str = r"common/index_mapping/{index_name}.json"

    # Путь к файлу с данными состояния
    PATH_STATE_JSON: str = r"state/etl_state_{index_name}.json"

    # Путь к логгам
    PATH_LOGS: str = r"logs/etl_log.log"

    # Host для подключения к Elasticsearch
    ELASTICSEARCH_HOST: str = os.environ.get("ELASTICSEARCH_HOST")

    ES_INDEX_NAME: str = ""

    # Начальное время modfified
    DEFAULT_MODIFIED_TIME: datetime.datetime = datetime.datetime(2020, 1, 1)

    # Настройка ETL pipeline
    TIME_SLEEP: int = 60

    SCHEMA: str = "content"
    GENRE_DB_NAME: str = "genre"
    PERSON_DB_NAME: str = "person"
    FILM_WORK_DB_NAME: str = "film_work"
    PERSON_FILM_WORK_DB_NAME: str = "person_film_work"
    PERSON_ID_NAME: str = "person_id"
    GENRE_FILM_WORK_DB_NAME: str = "genre_film_work"
    GENRE_ID_NAME: str = "genre_id"

    MOVIES_INDEX: str = "movies"
    GENRES_INDEX: str = "genres"
    PERSONS_INDEX: str = "persons"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"
