"""
Тесты для модуля управления асинхронными сессиями базы данных.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from src.database import (
    create_async_engine_from_settings,
    engine,
    get_async_session,
)


def test_engine_creation() -> None:
    """Проверяет, что движок создается корректно."""
    assert isinstance(engine, AsyncEngine)


def test_create_async_engine_from_settings() -> None:
    """Проверяет функцию создания движка из настроек."""
    result = create_async_engine_from_settings()
    assert isinstance(result, AsyncEngine)


@pytest.mark.asyncio
async def test_get_async_session() -> None:
    """Проверяет, что генератор сессий возвращает асинхронную сессию."""
    async for session in get_async_session():
        assert isinstance(session, AsyncSession)
        break  # Одна итерация
