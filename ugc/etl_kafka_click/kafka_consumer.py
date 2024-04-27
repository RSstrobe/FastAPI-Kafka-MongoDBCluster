import logging

from kafka import KafkaConsumer


def get_kafka_consumer():
    logging.info('Prepare to create KafkaConsumer')

    kafka_consumer = KafkaConsumer(
        'player_progress',
        'player_settings_events',
        'click_events',
        bootstrap_servers=['kafka_ugc:9092'],
        auto_offset_reset='earliest',
        group_id='ETL_to_Clickhouse',
        enable_auto_commit=False
    )
    logging.info('KafkaConsumer created')

    return kafka_consumer
