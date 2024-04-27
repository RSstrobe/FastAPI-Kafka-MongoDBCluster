import json
import logging
from time import sleep

from pymongo import ASCENDING

from constants import ASSOCIATION_COLLECTION_TO_SCHEMA, ASSOCIATION_COLLECTION_TO_CH_TABLE
from clickehouse_client import get_clickhouse_client
from mongo_client import get_mongo_client
from config import settings


def convert_document_to_modeldata(document, colection_name):
    model_data_schema = ASSOCIATION_COLLECTION_TO_SCHEMA[colection_name]
    try:
        model_data = model_data_schema(**document)
    except Exception as e:
        logging.error(f'{e.__class__.__name__}:\n{str(e)=}')
        return None

    return model_data


def yield_docs(cursor, chunk_size, collection_name):
    chunk = []
    for idx, doc in enumerate(cursor):
        if idx % chunk_size == 0 and idx > 0:
            yield chunk
            del chunk[:]

        doc_as_model_data = convert_document_to_modeldata(doc, collection_name)
        if not doc_as_model_data:
            continue

        chunk.append(doc_as_model_data)
    yield chunk


def etl_data():
    with get_mongo_client() as mongo_client, get_clickhouse_client() as click_client:
        last_tables_updates_dt = {
            ch_table_name: None
            for ch_table_name in ASSOCIATION_COLLECTION_TO_CH_TABLE.values()
        }

        # Ищем последние события в таблицах Clickhouse
        for ch_table_name in last_tables_updates_dt:
            last_update = click_client.execute(
                f'SELECT event_dt FROM shard_db.{ch_table_name} ORDER BY event_dt DESC LIMIT 1'
            )
            if last_update:
                last_tables_updates_dt[ch_table_name] = last_update[0][0]

        while True:
            updates_info = json.dumps(last_tables_updates_dt, indent=4, default=str)
            logging.info(f'Check for updates. {updates_info}')

            for collection_name, schema in ASSOCIATION_COLLECTION_TO_SCHEMA.items():
                ch_table_name = ASSOCIATION_COLLECTION_TO_CH_TABLE[collection_name]
                ch_table_columns_as_str = ', '.join(schema.get_field_names())
                insert_sql_query = \
                    f'INSERT INTO shard_db.{ch_table_name} ({ch_table_columns_as_str}) VALUES'

                if last_tables_updates_dt[ch_table_name]:  # Если есть данные об обновлении
                    find_filter = {
                        'dt': {
                            '$gt': last_tables_updates_dt[ch_table_name]
                        }
                    }
                else:
                    find_filter = {}

                cursor = mongo_client.ugc[collection_name].find(
                    find_filter,
                    batch_size=settings.mongo_ch_etl_batch_size
                ).sort('dt', ASCENDING)

                chunks = yield_docs(cursor, settings.mongo_ch_etl_batch_size, collection_name)
                for chunk in chunks:
                    if chunk:  # если не пустой
                        try:
                            rows_to_insert = [
                                list(doc.dict().values())
                                for doc in chunk
                            ]
                            result = click_client.execute(
                                query=insert_sql_query,
                                params=rows_to_insert
                            )
                            if result == 0:
                                logging.error(
                                    'Error during insertion in CH. '
                                    f'Collection: {collection_name}. '
                                    f'Chunk: {str(rows_to_insert)}'
                                )

                            # Выставляем новую дату последнего обновления
                            last_update_db = chunk[-1].dt
                            last_tables_updates_dt[ch_table_name] = last_update_db
                        except Exception as e:
                            logging.error(f'{e.__class__.__name__}:\n{str(e)=}')

            sleep(5)


if __name__ == '__main__':
    etl_data()
