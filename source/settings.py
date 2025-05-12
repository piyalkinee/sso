from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent
CONF_PATH = BASE_DIR / "sso.conf"


class EnvironmentConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=CONF_PATH, env_file_encoding="utf-8", extra="ignore"
    )


class APIConfig(EnvironmentConfig):
    host: str = Field(default="0.0.0.0", alias="API_HOST")
    port: int = Field(default=9897, alias="API_PORT")
    ssl: bool = Field(default=True, alias="SSL")


class HTTPConfig(EnvironmentConfig):
    path_prefix: str = Field(default="/auth", alias="HTTP_PATH_PREFIX")


class PostgresConfig(EnvironmentConfig):
    host: str = Field(default="127.0.0.1", alias="POSTGRES_HOST")
    port: int = Field(default=5432, alias="POSTGRES_PORT")
    user: str = Field(default="user", alias="POSTGRES_USER")
    password: str = Field(default="password", alias="POSTGRES_PASSWORD")
    database: str = Field(default="database", alias="POSTGRES_DATABASE")


class AccessSecurityConfig(EnvironmentConfig):
    secret_key: str = "secret"
    algorithm: str = "HS256"
    access_token_ttl: int = 1020
    refresh_token_ttl: int = 31556926


class Settings(EnvironmentConfig):
    log_level: str = Field(default="DEBUG", alias="LOG_LEVEL")
    debug: bool = Field(default=True, alias="DEBUG")
    workers: int = Field(default=1, alias="WORKERS")

    api: APIConfig = Field(default_factory=APIConfig)
    http: HTTPConfig = Field(default_factory=HTTPConfig)
    postgres: PostgresConfig = Field(default_factory=PostgresConfig)
    access_security: AccessSecurityConfig = Field(default_factory=AccessSecurityConfig)


settings = Settings()
