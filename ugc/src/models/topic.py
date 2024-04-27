from typing import Dict

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class TopicConfig(BaseSettings):
    topic_name: str
    num_partitions: int
    replication_factor: int
    topic_configs: Dict[str, str]
    model_config = ConfigDict(strict=True)
