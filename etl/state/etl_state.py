"""
Модуль для работы с состоянием ETL процесса.
"""
import abc
import json
import datetime
from typing import Any, Dict

from common import logger, setting

state_logger = logger.ETLLogger()


class BaseStorage(abc.ABC):
    """
    Абстрактное хранилище состояния.

    Позволяет сохранять и получать состояние.
    Способ хранения состояния может варьироваться в зависимости
    от итоговой реализации. Например, можно хранить информацию
    в базе данных или в распределённом файловом хранилище.
    """

    @abc.abstractmethod
    def save_state(self, state: Dict[str, Any]) -> None:
        """Сохранить состояние в хранилище."""

    @abc.abstractmethod
    def retrieve_state(self) -> Dict[str, Any]:
        """Получить состояние из хранилища."""


class JsonFileStorage(BaseStorage):
    """
    Реализация хранилища, использующего локальный файл.

    Формат хранения: JSON
    """

    def __init__(self, file_path: str) -> None:
        self.file_path = file_path

    def save_state(self, state: Dict[str, Any]) -> None:
        """
        Сохранить состояние в хранилище.
        """
        with open(self.file_path, "w") as fp:
            json.dump(state, fp)

    def retrieve_state(self) -> Dict[str, Any]:
        """
        Получить состояние из хранилища.
        """
        try:
            fp = open(self.file_path, "r")
        except FileNotFoundError:
            data = {}
        else:
            with fp:
                data = json.load(fp)
        return data


class State:
    """
    Класс для работы с состояниями.
    """

    def __init__(self, storage: BaseStorage) -> None:
        self.storage: BaseStorage = storage
        self.settings: setting = setting.Settings()
        self.is_first_run: bool = self.is_first_run()
        self.current_time: datetime.datetime = datetime.datetime.now().replace(
            second=0, microsecond=0
        )

    def set_state(self, key: str, value: Any) -> None:
        """
        Установить состояние для определённого ключа.
        """
        data = self.storage.retrieve_state()
        data[key] = value
        self.storage.save_state(data)

    def get_state(self, key: str) -> Any:
        """
        Получить состояние по определённому ключу.
        """
        data = self.storage.retrieve_state()
        state = data.get(key)

        return state

    def is_first_run(self) -> bool:
        """
        Проверка на первый запуск ETL.
        """
        state_logger.logger.info("Checking first run")

        is_first_run: bool = False

        first_run_value = self.get_state("is_first_run")

        if not first_run_value:
            is_first_run = True
            state_logger.logger.info("This run is first")
        else:
            state_logger.logger.info("This run isn't first")

        return is_first_run

    def create_state(self, data: Dict[str, str]) -> None:
        """
        Метод для создания состояния.

        :param data: данные для состояния
        """
        state_logger.logger.info("Creating state")

        state = {
            "is_first_run": self.is_first_run,
            "modfied": str(self.settings.DEFAULT_MODIFIED_TIME),
            "started_time": str(self.current_time),
            "data": data,
        }

        self.storage.save_state(state)

        state_logger.logger.info("State created. Path: %s", self.storage.file_path)
