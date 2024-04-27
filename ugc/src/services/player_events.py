import asyncio

from broker.base import BaseBrokerProducer
from broker.kafka import get_kafka_producer
from models.player import PlayerProgress, PlayerSettingEvents
from .base import BaseDataService


class PlayerService(BaseDataService):
    """Service for view progress of players"""

    def __init__(self, producer: BaseBrokerProducer):
        super().__init__(client=producer)

    async def send_message(self, topic_name: str, message_model: PlayerProgress | PlayerSettingEvents):
        """Send message to Kafka topic"""
        await self.client.produce(topic=topic_name, message=message_model)


def get_player_service():
    return PlayerService(producer=get_kafka_producer())
