from pathlib import Path

from pydantic import Field, KafkaDsn, MongoDsn
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parents[4]


class _BaseSettings(BaseSettings):
    """Changing the base class settings"""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class CommonSettings(_BaseSettings):
    """Base settings for service"""

    service_name: str = Field(default="ugc", description="Name of service")
    log_path: str = Field(default="logs/ugc_logs.log", description="Path log")


class AuthJWTSettings(_BaseSettings):
    """JWT settings for check privileges"""

    public_key: Path = Path(__file__).parent / "certs" / "public.pem"
    auth_algorithm_password: str = Field(
        default="RS256",
        description="Token encryption algorithm",
    )
    access_token_lifetime: int = Field(
        default=3600,
        description="Lifetime of access tokens in seconds",
    )
    refresh_token_lifetime: int = Field(
        default=86400,
        description="Refresh token lifetime in seconds",
    )


class KafkaSettings(_BaseSettings):
    """Kafka settings for service"""
    kafka_host: str = Field(
        default="localhost",
        description="Kafka host",
    )
    kafka_port: int = Field(
        default=9092,
        description="Kafka port",
    )


class MongoDBSettings(_BaseSettings):
    """Mongo settings for service"""
    mongodb_uri: MongoDsn = Field(
        default="mongodb://localhost:27019",
        description="Mongo url",
    )
    mongodb_db_name: str = Field(default="ugc", description="Mongo db name")


class Settings(CommonSettings):
    """Main class for combine settings"""

    auth_jwt: AuthJWTSettings = AuthJWTSettings()
    kafka: KafkaSettings = KafkaSettings()
    mongodb: MongoDBSettings = MongoDBSettings()


settings = Settings()
