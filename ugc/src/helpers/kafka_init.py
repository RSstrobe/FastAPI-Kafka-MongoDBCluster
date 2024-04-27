import json
from typing import Final

from kafka.admin import KafkaAdminClient, NewTopic

from core.config import settings
from helpers import logger
from models.topic import TopicConfig

kafka_logger = logger.UGCLogger()


def get_topic_json_config(path_to_json: str) -> dict:
    with open(path_to_json, "r") as fp:
        index_mapping = json.load(fp)
    return index_mapping


TOPIC_LIST: Final[list] = ["click_events", "player_settings_events", "player_progress"]


class KafkaInit:
    def __init__(self):
        self.topics_list = []
        self.admin_client = KafkaAdminClient(
            bootstrap_servers=f"{settings.kafka.kafka_host}:{settings.kafka.kafka_port}",
            client_id='test'
        )

    def append_topic(self, topic_config: TopicConfig):
        if topic_config.topic_name not in self.admin_client.list_topics():
            self.topics_list.append(
                NewTopic(
                    name=topic_config.topic_name,
                    num_partitions=topic_config.num_partitions,
                    replication_factor=topic_config.replication_factor,
                    topic_configs=topic_config.topic_configs,
                )
            )

    def create_topics(self):
        for this_topic in TOPIC_LIST:
            try:
                json_config = get_topic_json_config(f"core/topic_config/{this_topic}.json")
                topic_config = TopicConfig(**json_config)
                self.append_topic(topic_config=topic_config)
                kafka_logger.logger.info(f"Topic {topic_config.topic_name} appended")
            except Exception:
                kafka_logger.logger.error(f"Topic {topic_config.topic_name} didn't append")
        try:
            self.admin_client.create_topics(new_topics=self.topics_list, validate_only=False)
            kafka_logger.logger.info(f"All topics created")
        except Exception:
            kafka_logger.logger.error(f"Topics didn't create")


def get_kafka_init() -> KafkaInit:
    return KafkaInit()
