import logging

from pydantic_settings import BaseSettings


logging.basicConfig(
    level=logging.INFO,
    filename="log.log",
    filemode="w")


class Settings(BaseSettings):
    clickhouse_host_for_etl: str = ...
    clickhouse_username: str = ...
    clickhouse_password: str = ...
    kafka_ch_etl_batch_size: int = ...

    class Config:
        extra = 'allow'
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
