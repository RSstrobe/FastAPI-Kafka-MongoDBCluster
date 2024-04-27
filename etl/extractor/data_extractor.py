"""
Модуль для чтения данных из Postgres.
"""
import datetime
from uuid import UUID
from typing import Tuple, List, Any, Union, Optional, Iterator, Dict, Callable
from contextlib import closing
from itertools import chain

import psycopg2
from psycopg2.extras import RealDictRow, RealDictCursor

from . import readers
from common import setting
from common import logger
from common import backoff
from state.etl_state import State

extractor_logger = logger.ETLLogger()


class DataExtractor:
    """
    Класс Extractor - отвечает за чтение данных из Postgres в ETL процессе.
    """

    def __init__(self, state: State, settings: setting.Settings) -> None:
        self.state: State = state
        self.cursor: Optional[RealDictCursor] = None
        self.settings: setting = settings
        self.ref_datetime: datetime.datetime = self.get_ref_datetime()
        self.start_reader: Callable[
            [], Iterator[Union[List[Any], List[RealDictRow]]]
        ] = self.get_reader()

    def get_ref_datetime(self) -> datetime.datetime:
        """
        Метод получения времени, после которого будем считать записи измененными.

        :return: modified datetime
        """
        extractor_logger.logger.info("Start to get modified datetime")

        modified_datetime = self.settings.DEFAULT_MODIFIED_TIME

        if not self.state.is_first_run:
            started_datetime = self.state.get_state("started_time")
            modified_datetime = datetime.datetime.fromisoformat(started_datetime)

        extractor_logger.logger.info("Modified datetime - %s", modified_datetime)

        return modified_datetime

    def get_reader(self) -> Callable[[], Iterator[Union[List[Any], List[RealDictRow]]]]:
        """
        Метод получения итератора с данными для обработки.

        :return: итератор с данными для обработки
        """
        reader = []

        if self.settings.ES_INDEX_NAME == self.settings.MOVIES_INDEX:
            reader = self.start_reader_movies_index
        elif self.settings.ES_INDEX_NAME == self.settings.GENRES_INDEX:
            reader = self.start_reader_genres_index
        elif self.settings.ES_INDEX_NAME == self.settings.PERSONS_INDEX:
            reader = self.start_reader_persons_index

        return reader

    def get_modified_ids_from_main_table(
        self, db_name: str = "film_work"
    ) -> Iterator[Tuple[UUID, ...]]:
        """
        Метод получения id произведений по измененным состояниям произведений.

        :param db_name: таблица БД

        :return: кортеж с измененных id произведений
        """
        last_cursor_value_modif_fw_ids: Optional[str] = ""

        while last_cursor_value_modif_fw_ids is not None:

            res_full_data = readers.get_modified_common_ids(
                cursor=self.cursor,
                schema=self.settings.SCHEMA,
                db_name=db_name,
                ref_datetime=self.ref_datetime,
                previous_id=last_cursor_value_modif_fw_ids,
            )

            for row_batch in res_full_data:
                if not row_batch[0]:
                    last_cursor_value_modif_fw_ids = None
                    continue

                _, tuple_modif_fw_ids = row_batch

                last_cursor_value_modif_fw_ids = self.get_last_cursor(
                    tuple_modif_fw_ids
                )

                yield tuple_modif_fw_ids

    @staticmethod
    def get_last_cursor(data: List[UUID]) -> Optional[str]:
        """
        Метод получения последнего значения курсора.

        :return: значение курсора
        """
        if not data:
            return None

        return str(data[-1])

    def get_modified_ids_from_side_table(
        self, schema: str, db_name: str, db_name_relation: str, entity_id_name: str
    ) -> Tuple[UUID, ...]:
        """
        Метод для получения id произведений по измененным состоянием персоналий или жанров.

        :param schema: схема БД
        :param db_name: таблица БД (person, ganre)
        :param db_name_relation: таблица БД, связывающая сущности film_work и genre/person
        :param entity_id_name: название id сущности

        :return: кортеж с измененных id произведений
        """
        last_cursor_value_modif_ids: Optional[str] = ""
        last_cursor_value_modif_fw_ids: Optional[str] = ""

        while last_cursor_value_modif_ids is not None:
            res_modif_ids = readers.get_modified_common_ids(
                cursor=self.cursor,
                schema=schema,
                db_name=db_name,
                ref_datetime=self.ref_datetime,
                previous_id=last_cursor_value_modif_ids,
            )

            for row_batch in res_modif_ids:
                if not row_batch[0]:
                    last_cursor_value_modif_ids = None
                    continue

                _, tuple_modif_ids = row_batch
                last_cursor_value_modif_ids = self.get_last_cursor(tuple_modif_ids)

                _, tuple_modif_fw_ids = readers.get_modified_film_work_ids(
                    cursor=self.cursor,
                    schema=schema,
                    db_name=db_name_relation,
                    entity_id_name=entity_id_name,
                    ids_to_find=tuple_modif_ids,
                    previous_id=last_cursor_value_modif_fw_ids,
                )

                yield tuple_modif_fw_ids

    def get_modified_ids(self) -> Iterator[Tuple[UUID, ...]]:
        """
        Метод для получения измененных id произведений после заданного modified из всех таблиц.
        """
        extractor_logger.logger.info("Starting to get batch modified ids")

        tuple_ids_from_person = self.get_modified_ids_from_side_table(
            schema=self.settings.SCHEMA,
            db_name=self.settings.PERSON_DB_NAME,
            entity_id_name=self.settings.PERSON_ID_NAME,
            db_name_relation=self.settings.PERSON_FILM_WORK_DB_NAME,
        )

        tuple_ids_from_genres = self.get_modified_ids_from_side_table(
            schema=self.settings.SCHEMA,
            db_name=self.settings.GENRE_DB_NAME,
            entity_id_name=self.settings.GENRE_ID_NAME,
            db_name_relation=self.settings.GENRE_FILM_WORK_DB_NAME,
        )
        tuple_ids_from_film_work = self.get_modified_ids_from_main_table()

        modified_ids = chain(
            tuple_ids_from_person, tuple_ids_from_genres, tuple_ids_from_film_work
        )

        for modified_id_batch in modified_ids:
            yield modified_id_batch

        extractor_logger.logger.info("Ending to get batch modified ids")

    def get_modified_ids_from_filmwork(self) -> Iterator[Tuple[UUID, ...]]:
        """
        Метод для получения измененных id произведений после заданного modified из таблицы film_work.

        :param schema: схема БД
        :param db_name: Имя БД
        :param db_name_relation:
        :param entity_id_name:
        :return:
        """
        last_cursor_value_modif_ids: Optional[str] = ""

        while last_cursor_value_modif_ids is not None:
            res_modif_ids = readers.get_modified_person_ids_from_film_work(
                cursor=self.cursor,
                ref_datetime=self.ref_datetime,
                previous_id=last_cursor_value_modif_ids,
            )

            for row_batch in res_modif_ids:
                if not row_batch[0]:
                    last_cursor_value_modif_ids = None
                    continue

                _, tuple_modif_ids = row_batch
                last_cursor_value_modif_ids = self.get_last_cursor(tuple_modif_ids)

                yield tuple_modif_ids

    def get_full_data(self, modified_ids: Tuple[UUID, ...]) -> List[RealDictRow]:
        """
        Метод для получения информации по кинопроизведениям

        :param modified_ids: кортеж с измененными id произведений

        :return: кортеж с необработанной информацией по измененным кинопроизведениям
        """
        res_full_data = []
        if self.settings.ES_INDEX_NAME == self.settings.MOVIES_INDEX:
            res_full_data = readers.get_full_data(
                cursor=self.cursor, ids_to_find=modified_ids
            )
        elif self.settings.ES_INDEX_NAME == self.settings.PERSONS_INDEX:
            res_full_data = readers.get_full_data_persons(
                cursor=self.cursor, ids_to_find=modified_ids
            )

        return res_full_data

    @backoff.etl_backoff
    def start_reader_movies_index(
        self,
    ) -> Iterator[Union[List[Any], List[RealDictRow]]]:
        """
        Метод для старта чтения данных из Postgres.
        """

        extractor_logger.logger.info("Starting extractor process for movies index")

        dsn: Dict[str, Any] = {
            "dbname": self.settings.DB_NAME,
            "user": self.settings.DB_USER,
            "password": self.settings.DB_PASSWORD,
            "host": self.settings.DB_HOST,
            "port": self.settings.PORT,
        }

        with closing(psycopg2.connect(**dsn, cursor_factory=RealDictCursor)) as pg_conn:
            self.cursor = pg_conn.cursor()

            # id всех измененных произведений
            modified_ids = self.get_modified_ids()

            for this_batch_modified_ids in modified_ids:
                # Необходимая информация
                res_full_data = self.get_full_data(modified_ids=this_batch_modified_ids)
                yield res_full_data

        extractor_logger.logger.info("Ending extractor process for movies index")

    @backoff.etl_backoff
    def start_reader_genres_index(
        self,
    ) -> Iterator[Union[List[Any], List[RealDictRow]]]:

        extractor_logger.logger.info("Starting extractor process for genres index")

        dsn: Dict[str, Any] = {
            "dbname": self.settings.DB_NAME,
            "user": self.settings.DB_USER,
            "password": self.settings.DB_PASSWORD,
            "host": self.settings.DB_HOST,
            "port": self.settings.PORT,
        }

        last_cursor_value: Optional[str] = ""

        with closing(psycopg2.connect(**dsn, cursor_factory=RealDictCursor)) as pg_conn:
            self.cursor = pg_conn.cursor()

            while last_cursor_value is not None:
                res_modif_ids = readers.get_modified_common_ids(
                    cursor=self.cursor,
                    schema=self.settings.SCHEMA,
                    db_name=self.settings.GENRE_DB_NAME,
                    ref_datetime=self.ref_datetime,
                    previous_id=last_cursor_value,
                )

                for row_batch in res_modif_ids:
                    if not row_batch[0]:
                        last_cursor_value = None
                        continue

                    genres_batch, tuple_modif_ids = row_batch
                    last_cursor_value = self.get_last_cursor(tuple_modif_ids)

                    yield genres_batch

        extractor_logger.logger.info("Ending extractor process for genres index")

    @backoff.etl_backoff
    def start_reader_persons_index(
        self,
    ) -> Iterator[Union[List[Any], List[RealDictRow]]]:
        extractor_logger.logger.info("Starting extractor process for persons index")

        dsn: Dict[str, Any] = {
            "dbname": self.settings.DB_NAME,
            "user": self.settings.DB_USER,
            "password": self.settings.DB_PASSWORD,
            "host": self.settings.DB_HOST,
            "port": self.settings.PORT,
        }

        with closing(psycopg2.connect(**dsn, cursor_factory=RealDictCursor)) as pg_conn:
            self.cursor = pg_conn.cursor()

            tuple_ids_from_filmwork = self.get_modified_ids_from_filmwork()
            tuple_ids_from_person = self.get_modified_ids_from_main_table()

            modified_ids = chain(tuple_ids_from_filmwork, tuple_ids_from_person)

            for modified_id_batch in modified_ids:
                res_full_data = self.get_full_data(modified_ids=modified_id_batch)
                yield res_full_data

        extractor_logger.logger.info("Ending extractor process for persons index")
