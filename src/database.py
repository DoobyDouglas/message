"""
Модуль для управления асинхронными сессиями базы данных.

Содержит создание асинхронного движка SQLAlchemy, фабрику сессий
и dependency для FastAPI для получения сессий в роутах.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.config.settings import DatabaseSettings, get_database_settings
from src.models.base import Base

# Глобальные настройки базы данных
database_settings: DatabaseSettings = get_database_settings()


def create_async_engine_from_settings() -> AsyncEngine:
    """Создает асинхронный движок SQLAlchemy на основе настроек базы данных.

    Returns:
        Асинхронный движок SQLAlchemy.
    """
    return create_async_engine(
        database_settings.database_url,
        echo=False,
        future=True,
    )


engine = create_async_engine_from_settings()


async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Генератор асинхронных сессий для использования в качестве dependency FastAPI.

    Yields:
        Асинхронная сессия SQLAlchemy.
    """
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


async def create_tables() -> None:
    """Создает все таблицы в базе данных на основе декларативных моделей.

    Используется в тестах или при инициализации приложения.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
