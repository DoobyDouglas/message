"""
Конфигурация pytest с фикстурами для тестирования.

Содержит фикстуры для работы с тестовой базой данных, очистки таблиц
и создания тестового клиента FastAPI.
"""

import asyncio
from collections.abc import AsyncGenerator, Generator
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from src.config.settings import DatabaseSettings, get_database_settings
from src.database import get_async_session
from src.models.base import Base
from src.routes.system import router as system_router
from src.routes.users import router as users_router

# Глобальные настройки базы данных
database_settings: DatabaseSettings = get_database_settings()


def pytest_configure() -> None:
    """Конфигурация pytest для использования асинхронных тестов."""
    pytest.asyncio_fixture = pytest_asyncio.fixture


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Создает event loop для асинхронных тестов.

    Фикстура уровня сессии для повторного использования event loop.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine() -> AsyncGenerator[AsyncEngine, None]:
    """Создает асинхронный движок для тестовой базы данных."""
    engine = create_async_engine(
        database_settings.database_url,
        echo=False,
        future=True,
        poolclass=NullPool,  # Не используем пул для тестов
    )

    # Создаем таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Закрываем движок после всех тестов
    await engine.dispose()


@pytest.fixture
async def test_session(test_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """Создает асинхронную сессию для тестов."""
    async_session_factory = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )
    
    async with async_session_factory() as session:
        yield session


@pytest.fixture
def test_app(test_session: AsyncSession) -> FastAPI:
    """Создает тестовое приложение FastAPI с переопределенными зависимостями."""
    
    @asynccontextmanager
    async def test_lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
        """Lifespan для тестов без миграций."""
        # Не запускаем миграции в тестах
        yield
    
    # Создаем новое приложение для тестов
    app = FastAPI(
        title="Безымянный мессенджер (Тесты)",
        description="Тестовое приложение мессенджера",
        version="0.1.0",
        lifespan=test_lifespan,
    )
    
    # Переопределяем зависимость для использования тестовой сессии
    async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
        yield test_session
    
    app.dependency_overrides[get_async_session] = override_get_async_session
    
    # Подключаем роутеры
    app.include_router(system_router)
    app.include_router(users_router)
    
    return app


@pytest.fixture
def test_client(test_app: FastAPI) -> Generator[TestClient, None, None]:
    """Создает тестовый клиент FastAPI."""
    with TestClient(test_app) as client:
        yield client


@pytest.fixture
def mock_async_session() -> AsyncMock:
    """Создает мок асинхронной сессии для unit тестов."""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def mock_password_hasher() -> MagicMock:
    """Создает мок PasswordHasher для unit тестов."""
    hasher = MagicMock()
    hasher.verify_password = MagicMock(return_value=True)
    hasher.hash_password = MagicMock(return_value="hashed_password")
    return hasher


@pytest.fixture
def unique_email() -> str:
    """Генерирует уникальный email для тестов."""
    import uuid
    return f"test_{uuid.uuid4().hex[:8]}@example.com"