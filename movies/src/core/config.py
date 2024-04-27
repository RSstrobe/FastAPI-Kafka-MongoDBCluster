import os
from pathlib import Path
from logging import config as logging_config

from dotenv import load_dotenv, find_dotenv
from pydantic import BaseSettings, Field

from core.logger import LOGGING

load_dotenv(find_dotenv())
logging_config.dictConfig(LOGGING)


class _BaseSettings(BaseSettings):
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class CommonSettings(_BaseSettings):
    """Base project settings related to non-code parameters."""

    project_name: str = Field(
        default="movies",
        description="Название проекта. Используется в Swagger-документации.",
    )
    base_dir: str = Field(
        default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        description="Корень проекта",
    )


class AuthJWTSettings(_BaseSettings):
    private_key: Path = Path(__file__).parent / "certs" / "private.pem"
    public_key: Path = Path(__file__).parent / "certs" / "public.pem"
    auth_algorithm_password: str = Field(
        default="RS256",
        description="Алгоритм шифрования токена",
    )
    access_token_lifetime: int = Field(
        default=3600,
        description="Время жизни access токенов в секундах",
    )
    refresh_token_lifetime: int = Field(
        default=86400,
        description="Время жизни refresh токена в секундах",
    )


class RedisSettings(_BaseSettings):
    """Base redis settings."""

    redis_host: str = Field(default="localhost", description="Адрес хоста Redis")
    redis_port: int = Field(default=6379, description="Порт Redis")
    redis_database: str = Field(default="0", description="База данных Redis")
    redis_time_save_cache: int = Field(default=300, description="Время хранения кэша")


class ElasticSettings(_BaseSettings):
    """Base Elasticsearch settings."""

    elastic_host: str = Field(
        default="127.0.0.1",
        description="Адрес хоста Elasticsearch",
    )
    elastic_port: int = Field(default=9200, description="Порт Elasticsearch")


class PaginationSettings(_BaseSettings):
    """Base project settings related to pagination parameters."""

    page_size: int = Field(
        default=50,
        description="Количество произведений на странице",
    )
    max_page_size: int = Field(
        default=100,
        description="Максимальное количество произведений на странице",
    )
    max_page: int = Field(default=100, description="Максимальное количество страниц")
    batch_size_for_films_by_simular_genre: int = Field(
        default=5,
        description="Размер батча для endpoint: /api/v1/film/",
    )


class BackendSettings(_BaseSettings):
    """Base backend settings related to FastAPI parameters."""

    backend_fastapi_host: str = Field(
        default="0.0.0.0",
        description="Адрес хоста сервера",
    )
    backend_fastapi_port: int = Field(default=8000, description="Порт сервера")


class JaegerSettings(_BaseSettings):
    jaeger_host: str = Field(
        default="jaeger",
    )
    jaeger_port: int = Field(
        default=6831,
    )


class Settings(CommonSettings):
    """Main settings class for grouping other settings."""

    auth_jwt: AuthJWTSettings = AuthJWTSettings()
    redis: RedisSettings = RedisSettings()
    elastic: ElasticSettings = ElasticSettings()
    pagination: PaginationSettings = PaginationSettings()
    backend: BackendSettings = BackendSettings()
    jaeger: JaegerSettings = JaegerSettings()


settings = Settings()
