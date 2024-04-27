from aiokafka import AIOKafkaProducer
from pydantic import BaseModel

from .base import BaseBrokerProducer
from core.config import settings

class KafkaBrokerProducer(BaseBrokerProducer):
    """Kafka producer for sending messages to kafka topic"""

    def __init__(self, client: AIOKafkaProducer):
        self.client = client

    async def produce(self, topic: str, message: BaseModel):
        """Send message to kafka topic"""
        await self.client.start()
        await self.client.send(
            topic=topic, value=message.model_dump_json().encode("utf-8")
        )
        await self.client.stop()


def get_kafka_producer() -> KafkaBrokerProducer:
    """Get kafka producer"""
    return KafkaBrokerProducer(
        client=AIOKafkaProducer(
            bootstrap_servers=f"{settings.kafka.kafka_host}:{settings.kafka.kafka_port}",
            client_id='test'
        )
    )
