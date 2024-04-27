import json
import logging

from clickehouse_publisher import get_clickhouse_client
from config import settings
from constants import ASSOCIATION_TOPIC_TO_SCHEMA

from kafka import TopicPartition, OffsetAndMetadata
from kafka_consumer import get_kafka_consumer, KafkaConsumer


def convert_msg_to_modeldata(message_value, topic_name):
    model_data_schema = ASSOCIATION_TOPIC_TO_SCHEMA[topic_name]
    try:
        model_data = model_data_schema(**message_value)
    except Exception as e:
        logging.error(f'{e.__class__.__name__}:\n{str(e)=}')
        return None

    return model_data


def consume_messages(consumer: KafkaConsumer):
    logging.info("ETL started.")

    topics_data = {
        'player_progress': {
            'message_count': 0,
            'rows_to_insert': [],
            'offsets': None
        },
        'player_settings_events': {
            'message_count': 0,
            'rows_to_insert': [],
            'offsets': None

        },
        'click_events': {
            'message_count': 0,
            'rows_to_insert': [],
            'offsets': None
        },
    }

    for message in consumer:
        topic_name = message.topic
        logging.info(f'Get message from {topic_name}')
        topics_data[message.topic]['message_count'] += 1
        logging.info(f'Messages count {topic_name}: {topics_data[message.topic]["message_count"]}')

        if topics_data[topic_name]['offsets'] is None:
            topics_data[topic_name]['offsets'] = {
                TopicPartition(topic_name, message.partition): OffsetAndMetadata(message.offset+settings.kafka_ch_etl_batch_size, '')
            }

        try:
            message_value = json.loads(message.value.decode('ascii'))

            if isinstance(message_value, dict):
                model_data = convert_msg_to_modeldata(message_value, topic_name)
                if model_data:
                    row_to_insert = list(model_data.dict().values())
                    topics_data[message.topic]['rows_to_insert'].append(row_to_insert)
            else:
                logging.error(
                    'Message value should be Dict instance!'
                    f'{topic_name}:\n{message_value}'
                )
        except Exception as e:
            logging.error(f'{str(e)}\n{topic_name}:\n{message.value}')

        if topics_data[message.topic]['message_count'] >= settings.kafka_ch_etl_batch_size:
            logging.info(f'Prepare to bulk insert into {topic_name!r} table')

            table_columns_as_str = ', '.join(dict(model_data).keys())
            sql_query = \
                f'INSERT INTO shard_db.{topic_name} ({table_columns_as_str}) VALUES'

            clickhouse_client = get_clickhouse_client()
            try:
                clickhouse_client.execute(
                    query=sql_query,
                    params=topics_data[message.topic]['rows_to_insert'])

                topics_data[message.topic]['rows_to_insert'] = []

                # Смещаем курсор
                consumer.commit(offsets=topics_data[topic_name]['offsets'])
                topics_data[topic_name]['offsets'] = None
                topics_data[message.topic]['message_count'] = 0

            except Exception as e:
                logging.error(f'{e.__class__.__name__}:\n{str(e)=}')


if __name__ == '__main__':
    consumer = get_kafka_consumer()
    consume_messages(consumer)
