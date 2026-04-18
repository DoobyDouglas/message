"""
Модуль настроек приложения.

Содержит классы для загрузки конфигурации из переменных окружения.
Использует pydantic для валидации и парсинга.
"""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """Настройки базы данных.

    Все параметры загружаются из переменных окружения с префиксом POSTGRES_.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "messenger"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432

    @property
    def database_url(self) -> str:
        """Возвращает URL для подключения к базе данных в формате SQLAlchemy."""
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    def get_alembic_config(self) -> dict[str, str]:
        """Возвращает конфигурацию для Alembic.

        Returns:
            Словарь с ключом 'sqlalchemy.url' для использования в alembic.ini
        """
        return {"sqlalchemy.url": self.database_url}


class AuthSettings(BaseSettings):
    """Настройки аутентификации и JWT.

    Все параметры загружаются из переменных окружения с префиксом JWT_.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    JWT_SECRET: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    SESSION_EXPIRE_DAYS: int = 30
    COOKIE_SECURE: bool = False
    COOKIE_SAMESITE: Literal["lax", "strict", "none"] = "lax"
    COOKIE_HTTPONLY: bool = True


@lru_cache(maxsize=1)
def get_database_settings() -> DatabaseSettings:
    """Возвращает экземпляр настроек базы данных с кэшированием."""
    return DatabaseSettings()


@lru_cache(maxsize=1)
def get_auth_settings() -> AuthSettings:
    """Возвращает экземпляр настроек аутентификации с кэшированием."""
    return AuthSettings()
