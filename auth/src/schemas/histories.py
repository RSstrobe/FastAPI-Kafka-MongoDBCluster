from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field

from schemas.base import BaseModelPaginationFilter


class HistoryBase(BaseModel):
    user_id: UUID = Field(comment="Идентификатор пользователя")
    device_id: str | None = Field(
        default=None, comment="Идентификатор девайса пользователя"
    )


class IdHistorySchema(HistoryBase):
    id: UUID = Field(comment="Идентификатор сессии пользователя")


class FullHistorySchema(HistoryBase):
    dt_login: datetime | None = Field(
        default=datetime.now(), comment="Дата и время входа пользователя"
    )
    dt_logout: datetime | None = Field(
        default=None, comment="Дата и время выхода пользователя"
    )


class FullIdHistorySchema(IdHistorySchema, FullHistorySchema):
    pass


class HistoryRequestSchema(BaseModelPaginationFilter):
    pass
