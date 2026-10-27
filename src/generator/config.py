"""Настройки генератора и подключения к ClickHouse.

Значения читаются из переменных окружения и файла .env.
Приоритет: переменные окружения > .env > значения по умолчанию.
"""

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class _EnvSettings(BaseSettings):
    """Общая база: откуда читать и как относиться к лишним переменным."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class GeneratorSettings(_EnvSettings):
    """Параметры самого генератора (префикс GENERATOR_)."""

    model_config = SettingsConfigDict(env_prefix="GENERATOR_")

    seed: int = 42
    customers_count: int = Field(default=5000, ge=1)
    tick_interval_seconds: float = Field(default=1.0, gt=0)
    base_orders_per_minute: float = Field(default=30.0, gt=0)

    retry_max_attempts: int = Field(default=5, ge=1)
    retry_base_delay: float = Field(default=0.5, gt=0)
    retry_max_delay: float = Field(default=10.0, gt=0)


class ClickHouseSettings(_EnvSettings):
    """Параметры подключения к ClickHouse (префикс CLICKHOUSE_)."""

    model_config = SettingsConfigDict(env_prefix="CLICKHOUSE_")

    host: str = "localhost"
    port: int = Field(default=8123, ge=1, le=65535)
    database: str = "quantium"
    user: str = "quantium"
    password: SecretStr = SecretStr("")
