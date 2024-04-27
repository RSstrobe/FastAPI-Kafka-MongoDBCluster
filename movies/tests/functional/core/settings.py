from pydantic import Field, BaseSettings


class TestSettings(BaseSettings):
    elastic_host: str = Field("http://localhost")
    elastic_port: int = Field(9200)
    redis_host: str = Field("localhost")
    redis_port: int = Field(6379)
    redis_database: int = Field(0)
    redis_password: str = Field("password")
    service_url: str = Field("http://localhost:8000")


test_settings = TestSettings()
