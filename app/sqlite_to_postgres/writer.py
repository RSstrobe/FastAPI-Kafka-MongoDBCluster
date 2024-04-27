"""
Модуль для записи данных в PostgreSQL.
"""

from dataclasses import astuple, dataclass, fields
from typing import List

import const
import logger
from psycopg2.extensions import cursor
from psycopg2.extras import execute_batch

writer_logger = logger.SqliteToPostresqlLogger()


def write_data_to_pg(
    curs: cursor,
    data: List[dataclass],
    db_class: dataclass,
    db_name: str,
    schema: str = const.MOVIES_SCHEMA,
) -> None:
    """Основной метод для записи данных в PostgreSQL."""

    try:
        db_columns = [field.name for field in fields(db_class)]
        db_columns_str = ",".join(db_columns)
        col_count = ", ".join(["%s"] * len(db_columns))
        prepared_data = [astuple(row) for row in data]
        query = f"""
            insert into {schema}.{db_name} ({db_columns_str})
            values ({col_count})
            on conflict (id) do nothing;
            COMMIT;
        """

        execute_batch(curs, query, prepared_data, page_size=const.PAGE_SIZE)
    except Exception as error:
        writer_logger.logger.warning(f"Произошла ошибка записи данных: {error}.")
