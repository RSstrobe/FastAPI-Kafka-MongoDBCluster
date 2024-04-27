"""Модуль для хранения статичных переменных."""
import data_classes

# SQLite
CREATED_AT_NAME = "created_at"
UPDATED_AT_NAME = "updated_at"
CREATED_NAME = "created"
MODIFIED_NAME = "modified"
ADD_AS = "as"

# Tables
SQLITE_TABLES_DICT = {
    "genre": data_classes.Genre,
    "person": data_classes.Person,
    "film_work": data_classes.Filmwork,
    "genre_film_work": data_classes.GenreFilmwork,
    "person_film_work": data_classes.PersonFilmwork,
}

# PostreSQL
MOVIES_SCHEMA = "content"
PAGE_SIZE = 10
