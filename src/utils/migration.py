"""
Модуль для управления миграциями базы данных.

Предоставляет функцию для автоматического применения миграций при старте приложения.
"""

from pathlib import Path

from alembic import command
from alembic.config import Config

from src.config.settings import DatabaseSettings, get_database_settings

# Глобальные настройки базы данных
database_settings: DatabaseSettings = get_database_settings()


def get_alembic_config() -> Config:
    """Создаёт и возвращает конфигурацию Alembic."""
    # Получаем путь к корню проекта
    project_root = Path(__file__).parent.parent.parent
    alembic_ini_path = project_root / "alembic.ini"

    # Создаём конфигурацию Alembic
    config = Config(str(alembic_ini_path))

    # Устанавливаем URL базы данных из настроек приложения
    config.set_main_option("sqlalchemy.url", database_settings.database_url)

    return config


async def run_migrations() -> None:
    """Применяет все ожидающие миграции базы данных."""
    config = get_alembic_config()
    # Применяем миграции синхронно, дожидаясь завершения
    command.upgrade(config, "head")


def run_migrations_sync() -> None:
    """Синхронная версия функции run_migrations для использования вне
    асинхронного контекста."""
    config = get_alembic_config()
    command.upgrade(config, "head")
