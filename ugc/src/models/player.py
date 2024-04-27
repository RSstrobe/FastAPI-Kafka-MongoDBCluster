import datetime
from enum import Enum
from uuid import UUID

from pydantic import Field, model_validator

from models.base import KafkaModelConfig


class EventsNames(Enum):
    change_resolution_to_480 = "change_resolution_to_480"
    change_resolution_to_720 = "change_resolution_to_720"
    change_resolution_to_1080 = "change_resolution_to_1080"
    change_resolution_to_1440 = "change_resolution_to_1440"
    change_resolution_to_2160 = "change_resolution_to_2160"


class PlayerSettingEvents(KafkaModelConfig):
    user_id: str = Field(description="UUID пользователя")
    movie_id: str = Field(description="UUID произведения")
    event_dt: datetime.datetime = Field(default_factory=datetime.datetime.utcnow, description="Время события")
    event_type: int = Field(description="Тип события")


class PlayerProgress(KafkaModelConfig):
    user_id: str = Field(description="UUID пользователя")
    movie_id: str = Field(description="UUID произведения")
    event_dt: datetime.datetime = Field(default_factory=datetime.datetime.utcnow, description="Время события")
    view_progress: int = Field(description="Прогресс просмотра произведения в секундах")
    movie_duration: int = Field(description="Продолжительность произведения в секундах")

    @model_validator(mode='after')
    def compare_duration_and_view(self):
        if self.view_progress > self.movie_duration:
            raise ValueError("view_progress is larger than movie_duration")
        return self
