import uuid
import datetime
from typing import Annotated
from sqlalchemy.orm import DeclarativeBase, mapped_column
from sqlalchemy import String, text

str_50 = Annotated[str, 50]
str_256 = Annotated[str, 256]
intpk = Annotated[int, mapped_column(primary_key=True)]
uuidpk = Annotated[uuid.UUID, mapped_column(primary_key=True, default=uuid.uuid4)]
datetime_at_utc = Annotated[
    datetime.datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))
]


class Base(DeclarativeBase):
    type_annotation_map = {
        str_256: String(256),
        str_50: String(50),
    }

    repr_cols_num = 3
    repr_cols = tuple()

    def __repr__(self):
        cols = []
        for idx, col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_cols or idx < self.repr_cols_num:
                cols.append(f"{col}={getattr(self, col)}")

        return f"<{self.__class__.__name__} {', '.join(cols)}>"
