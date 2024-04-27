from sqlalchemy_utils import database_exists

from subsidiary.backoff import backoff


@backoff(connect_exception=ConnectionError)
def is_db_exist(pg_url: str):
    return database_exists(pg_url)


if __name__ == "__main__":
    pg_url = "postgresql://test_auth_user:test_auth_pass@auth-postgres-testing:5432/test_auth"
    is_db_exist(pg_url=pg_url)
