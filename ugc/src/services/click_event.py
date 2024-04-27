from broker.base import BaseBrokerProducer
from broker.kafka import get_kafka_producer
from models.click import ClickEvent
from .base import BaseDataService


class ClickService(BaseDataService):
    """Service for clicks of users events"""

    def __init__(self, client: BaseBrokerProducer):
        super().__init__(client=client)

    async def send_message(self, topic_name: str, message_model: ClickEvent):
        """Send message to Kafka topic"""
        await self.client.produce(topic=topic_name, message=message_model)


def get_click_service():
    return ClickService(client=get_kafka_producer())
