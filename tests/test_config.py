import pytest
from generator.config import ClickHouseSettings, GeneratorSettings
from pydantic import ValidationError


def test_generator_defaults() -> None:
    settings = GeneratorSettings(_env_file=None)
    assert settings.seed == 42
    assert settings.tick_interval_seconds == 1.0


def test_env_overrides_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GENERATOR_SEED", "7")
    settings = GeneratorSettings(_env_file=None)
    assert settings.seed == 7


def test_invalid_interval_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GENERATOR_TICK_INTERVAL_SECONDS", "0")
    with pytest.raises(ValidationError):
        GeneratorSettings(_env_file=None)


def test_password_is_hidden(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CLICKHOUSE_PASSWORD", "secret123")
    settings = ClickHouseSettings(_env_file=None)
    assert settings.password.get_secret_value() == "secret123"
    assert "secret123" not in repr(settings)
