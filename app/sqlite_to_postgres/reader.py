"""
Модуль для чтения данных из SQLite, PostgreSQL.
"""

import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass, fields
from typing import List

import const
import logger
import utils
from psycopg2.extensions import cursor

reader_logger = logger.SqliteToPostresqlLogger()


@contextmanager
def conn_context(db_path: str):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


def read_data_from_sqlite(
    curs: sqlite3.Cursor, db_class: dataclass, db_name: str
) -> List[dataclass]:
    """Метод чтения данных из SQLite."""

    try:
        db_columns = [utils.add_alias(field.name) for field in fields(db_class)]
        db_columns_str = ",".join(map(str, db_columns))

        query = f"""select {db_columns_str} from {db_name} order by id;"""
        curs.execute(query)
        result = [db_class(**dict(row)) for row in curs.fetchall()]
    except Exception as error:
        result = []
        reader_logger.logger.warning(f"Произошла ошибка чтения: {error}")

    return result


def read_data_from_postgres(
    curs: cursor,
    db_class: dataclass,
    db_name: str,
    schema: str = const.MOVIES_SCHEMA,
) -> List[dataclass]:
    """Метод чтения данных из PostgreSQL."""
    try:
        db_columns = [field.name for field in fields(db_class)]
        db_columns_str = ",".join(map(str, db_columns))

        query = f"""select {db_columns_str} from {schema}.{db_name} order by id;"""
        curs.execute(query)
        result = [db_class(**dict(row)) for row in curs.fetchall()]
    except Exception as error:
        result = []
        reader_logger.logger.warning(f"Произошла ошибка чтения: {error}")

    return result
