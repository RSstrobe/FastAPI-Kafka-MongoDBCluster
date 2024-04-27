"""Модуль для вспомогательных функций."""
import const


def add_alias(column_name: str):
    """Метод для добавления элиасов для корректного чтения данных из SQLite."""
    if column_name == const.CREATED_NAME:
        column_name = " ".join(
            (const.CREATED_AT_NAME, const.ADD_AS, const.CREATED_NAME)
        )
    elif column_name == const.MODIFIED_NAME:
        column_name = " ".join(
            (const.UPDATED_AT_NAME, const.ADD_AS, const.MODIFIED_NAME)
        )

    return column_name
