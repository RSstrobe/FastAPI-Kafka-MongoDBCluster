"""
Модуль для инициализации представления таблиц через dataclass.
"""
import datetime
import uuid
from dataclasses import dataclass, field

from dateutil.parser import parse


@dataclass
class Filmwork:
    title: str
    description: str
    creation_date: datetime.datetime
    rating: float
    type: str
    created: datetime.datetime
    modified: datetime.datetime
    file_path: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)

    def __post_init__(self):
        if not isinstance(self.creation_date, datetime.datetime):
            self.creation_date = (
                parse(self.creation_date)
                if self.creation_date is not None
                else self.creation_date
            )
        if not isinstance(self.created, datetime.datetime):
            self.created = parse(self.created)
        if not isinstance(self.modified, datetime.datetime):
            self.modified = parse(self.modified)
        if not isinstance(self.rating, float):
            self.rating = float(self.rating) if self.rating is not None else self.rating


@dataclass
class Genre:
    name: str
    description: str
    created: datetime.datetime
    modified: datetime.datetime
    id: uuid.UUID = field(default_factory=uuid.uuid4)

    def __post_init__(self):
        if not isinstance(self.created, datetime.datetime):
            self.created = parse(self.created)
        if not isinstance(self.modified, datetime.datetime):
            self.modified = parse(self.modified)


@dataclass
class PersonFilmwork:
    person_id: uuid.UUID
    film_work_id: uuid.UUID
    role: str
    created: datetime.datetime
    id: uuid.UUID = field(default_factory=uuid.uuid4)

    def __post_init__(self):
        if not isinstance(self.created, datetime.datetime):
            self.created = parse(self.created)


@dataclass
class GenreFilmwork:
    genre_id: uuid.UUID
    film_work_id: uuid.UUID
    created: datetime.datetime
    id: uuid.UUID = field(default_factory=uuid.uuid4)

    def __post_init__(self):
        if not isinstance(self.created, datetime.datetime):
            self.created = parse(self.created)


@dataclass
class Person:
    full_name: str
    created: datetime.datetime
    modified: datetime.datetime
    id: uuid.UUID = field(default_factory=uuid.uuid4)

    def __post_init__(self):
        if not isinstance(self.created, datetime.datetime):
            self.created = parse(self.created)
        if not isinstance(self.modified, datetime.datetime):
            self.modified = parse(self.modified)
