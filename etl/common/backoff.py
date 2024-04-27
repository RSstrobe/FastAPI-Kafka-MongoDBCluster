"""
Модуль настройки backoff.
"""
import backoff
import psycopg2
import elasticsearch

from common import logger

# Настройка backoff
BACKOFF_SETTINGS = {
    "wait_gen": backoff.expo,
    "exception": (psycopg2.OperationalError, elasticsearch.TransportError),
    "max_tries": 5,
    "max_time": 60 * 5,
    "logger": logger.ETLLogger().logger,
}

# не понимаю, почему не выводятся логи в консоль из backoff
etl_backoff = backoff.on_exception(**BACKOFF_SETTINGS)
