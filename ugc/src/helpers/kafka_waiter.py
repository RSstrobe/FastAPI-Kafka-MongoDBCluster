from kafka import KafkaConsumer

from helpers import logger
from backoff import backoff

kafka_logger = logger.UGCLogger()


@backoff((ConnectionError,), attempts=30)
def get_kafka_consumer():
    try:
        kafka_consumer = KafkaConsumer(
            bootstrap_servers=['kafka_ugc:9092'],
            auto_offset_reset='earliest',
            group_id='ETL_to_Clickhouse')

        topics = kafka_consumer.topics()
        kafka_logger.logger.info(f"{topics=}")

        if topics:
            return True
        return None
    except Exception:
        return None


if __name__ == '__main__':
    get_kafka_consumer()
