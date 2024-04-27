import logging

from socket import gaierror
from clickhouse_driver import Client
from clickhouse_driver.errors import NetworkError

from backoff import backoff
from config import settings


@backoff((ConnectionError,))
def wait_first_node():
    try:
        client = Client(host='clickhouse-node1',
                        user=settings.clickhouse_username,
                        password=settings.clickhouse_password)
        client.execute('SHOW DATABASES')
        logging.info("First node ready!")
        return True
    except Exception:
        return None


@backoff((ConnectionError,))
def wait_second_node():
    try:
        client = Client(host='clickhouse-node2',
                        user=settings.clickhouse_username,
                        password=settings.clickhouse_password)
        client.execute('SHOW DATABASES')
        logging.info('Second node ready!')
        return True
    except Exception:
        return None


@backoff((ConnectionError,))
def wait_third_node():
    try:
        client = Client(host='clickhouse-node3',
                        user=settings.clickhouse_username,
                        password=settings.clickhouse_password)
        client.execute('SHOW DATABASES')
        logging.info('Third node ready!')
        return True
    except Exception:
        return None


def main():
    wait_first_node()
    wait_second_node()
    wait_third_node()


if __name__ == '__main__':
    main()
