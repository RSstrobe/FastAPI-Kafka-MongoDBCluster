"""Модуль для хранения настроек."""
import os

from dotenv import load_dotenv

load_dotenv("../../.env")

DSL = {
    "dbname": os.environ.get("DB_NAME"),
    "user": os.environ.get("DB_USER"),
    "password": os.environ.get("DB_PASSWORD"),
    "host": os.environ.get("DB_HOST"),
    "port": os.environ.get("PORT", 5432),
}

SQLITE_NAME = os.environ.get("DB_PATH_SL")

APP_NAME = os.environ.get("DATA_TRANSFER_APP_NAME")
