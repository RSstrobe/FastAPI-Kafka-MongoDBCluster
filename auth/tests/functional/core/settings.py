from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings


class TestSettings(BaseSettings):
    postgres_database: str = Field(default="test_auth")
    postgres_user: str = Field(default="test_auth_user")
    postgres_password: str = Field(default="test_auth_pass")
    postgres_host: str = Field(default="localhost")
    postgres_port: int = Field(default=5432)
    redis_host: str = Field(default="redis-testing")
    redis_port: int = Field(default=6379)
    redis_database: int = Field(default=0)
    redis_password: str = Field(default="test_auth_pass")
    service_url: str = Field(default="http://localhost:8000")

    @property
    def database_url_asyncpg(self):
        return "postgresql+asyncpg://{}:{}@{}:{}/{}".format(
            self.postgres_user,
            self.postgres_password,
            self.postgres_host,
            self.postgres_port,
            self.postgres_database,
        )

    @property
    def database_url_psycopg(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql",
            username=self.postgres_user,
            password=self.postgres_password,
            host=self.postgres_host,
            port=self.postgres_port,
            path=self.postgres_database,
        )


test_settings = TestSettings()
