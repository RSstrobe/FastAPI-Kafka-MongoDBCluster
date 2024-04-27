import logging

from pydantic_settings import BaseSettings
from pydantic import Field 


logging.basicConfig(
    level=logging.INFO,
    filename="log.log",
    filemode="a")


class Settings(BaseSettings):
    clickhouse_username: str = ...
    clickhouse_password: str = ...

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
