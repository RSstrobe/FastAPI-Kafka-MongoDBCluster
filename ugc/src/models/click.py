import datetime

from pydantic import Field

from models.base import KafkaModelConfig


class ClickEvent(KafkaModelConfig):
    user_id: str = Field(description="UUID пользователя")
    movie_id: str = Field(description="UUID произведения")
    current_url: str = Field(default_factory=datetime.datetime.utcnow, description="Время события")
    destination_url: str | None = Field(description="Тип события")
