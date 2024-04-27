import logging
import time 

from clickhouse_driver import Client

from config import settings


def select_test():
    logging.info('Test running')
    first_client = Client(
        host='clickhouse-node3',
        user=settings.clickhouse_username,
        password=settings.clickhouse_password)
    first_client.execute(
        "INSERT INTO replica_db.player_progress \
        (user_id, movie_id, event_dt, view_progress, movie_duration) \
        VALUES (\
            '1c1884cc-17c8-4d6c-93c3-c4c385f468b5', \
            '251fd098-0965-4c79-8ab6-81404f9f9e37', \
            today(), \
            123, \
            456 \
        )")
    first_result = first_client.execute('SELECT * FROM replica_db.player_progress')
    logging.info(f'{first_result=}')
    second_client = Client(
        host='clickhouse-node1',
        user=settings.clickhouse_username,
        password=settings.clickhouse_password)

    # задержка, чтобы данные успели загрузиться в связанные таблицы
    time.sleep(2)

    second_result = second_client.execute('SELECT * FROM shard_db.player_progress')
    logging.info(f'{second_result=}')
    print(f'{second_result=}')
    if first_result == second_result:
        logging.info('Test successfully passed!')
    else:
        logging.info('Test completed with error!')


def main():
    try:
        select_test()
    except Exception as e:
        logging.error(f'{e.__class__.__name__}: \n {str(e)}')


if __name__ == '__main__':
    main()
