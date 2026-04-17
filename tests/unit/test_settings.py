"""
Тесты для модуля настроек приложения.
"""

import os
from unittest.mock import patch

from src.config.settings import DatabaseSettings, get_database_settings


class TestDatabaseSettings:
    """Тесты настроек базы данных."""

    def test_default_values(self):
        """Проверка значений по умолчанию."""
        settings = DatabaseSettings()
        assert settings.POSTGRES_USER == "postgres"
        assert settings.POSTGRES_PASSWORD == "postgres"
        assert settings.POSTGRES_DB == "messenger"
        assert settings.POSTGRES_HOST == "localhost"
        assert settings.POSTGRES_PORT == 5432

    def test_database_url_default(self):
        """Проверка формирования URL базы данных по умолчанию."""
        settings = DatabaseSettings()
        expected = "postgresql+asyncpg://postgres:postgres@localhost:5432/messenger"
        assert settings.database_url == expected

    def test_database_url_custom(self):
        """Проверка формирования URL базы данных с кастомными значениями."""
        # Используем model_construct для создания экземпляра без загрузки из окружения
        settings = DatabaseSettings.model_construct(
            POSTGRES_USER="user",
            POSTGRES_PASSWORD="pass",
            POSTGRES_DB="db",
            POSTGRES_HOST="host",
            POSTGRES_PORT=1234,
        )
        expected = "postgresql+asyncpg://user:pass@host:1234/db"
        assert settings.database_url == expected

    def test_get_alembic_config(self):
        """Проверка получения конфигурации для Alembic."""
        settings = DatabaseSettings()
        config = settings.get_alembic_config()
        assert config == {"sqlalchemy.url": settings.database_url}

    def test_load_from_env(self):
        """Проверка загрузки значений из переменных окружения."""
        with patch.dict(
            os.environ,
            {
                "POSTGRES_USER": "testuser",
                "POSTGRES_PASSWORD": "testpass",
                "POSTGRES_DB": "testdb",
                "POSTGRES_HOST": "testhost",
                "POSTGRES_PORT": "9999",
            },
        ):
            settings = DatabaseSettings()
            assert settings.POSTGRES_USER == "testuser"
            assert settings.POSTGRES_PASSWORD == "testpass"
            assert settings.POSTGRES_DB == "testdb"
            assert settings.POSTGRES_HOST == "testhost"
            assert settings.POSTGRES_PORT == 9999


def test_get_database_settings():
    """Проверка функции get_database_settings с кэшированием."""
    # Первый вызов должен создать экземпляр
    settings1 = get_database_settings()
    assert isinstance(settings1, DatabaseSettings)

    # Второй вызов должен вернуть тот же объект (кэширование)
    settings2 = get_database_settings()
    assert settings2 is settings1

    # Очистка кэша и проверка нового экземпляра
    get_database_settings.cache_clear()
    settings3 = get_database_settings()
    assert isinstance(settings3, DatabaseSettings)
    assert settings3 is not settings1
