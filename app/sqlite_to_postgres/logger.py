"""Модуль логирования."""

import logging

import setting


class SqliteToPostresqlLogger:
    def __init__(self):
        self.logger = logging.getLogger(setting.APP_NAME)
        logging.basicConfig(level=logging.INFO, filename="py_log.log", filemode="a")
