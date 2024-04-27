from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class KafkaModelConfig(BaseSettings):
    model_config = ConfigDict(populate_by_name=True)
