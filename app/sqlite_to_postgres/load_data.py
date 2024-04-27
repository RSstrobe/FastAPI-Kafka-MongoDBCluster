import os
from contextlib import contextmanager
import sqlite3

import const
import psycopg2
import reader
import writer
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor



DSL = {
    'dbname': os.environ.get('DB_NAME'),
    'user': os.environ.get('DB_USER'),
    'password': os.environ.get('DB_PASSWORD'),
    'host': os.environ.get('DB_HOST'),
    'port': os.environ.get('DB_PORT')
}

@contextmanager
def open_sqlite3_db(file_name: str):
    conn = sqlite3.connect(file_name)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.commit()
        conn.close()


def load_from_sqlite(connection: sqlite3.Connection, pg_conn: _connection):
    """Основной метод загрузки данных из SQLite в Postgres"""

    sqlite_curs = connection.cursor()
    pg_curs = pg_conn.cursor()

    for db_name, db_class in const.SQLITE_TABLES_DICT.items():
        sqlite_data = reader.read_data_from_sqlite(sqlite_curs, db_class, db_name)
        writer.write_data_to_pg(pg_curs, sqlite_data, db_class, db_name)


if __name__ == "__main__":
    with open_sqlite3_db('db.sqlite') as sqlite_conn, psycopg2.connect(**DSL, cursor_factory=DictCursor) as pg_conn:
        load_from_sqlite(sqlite_conn, pg_conn)
    pg_conn.close()
