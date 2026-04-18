"""
Конфигурация pytest с фикстурами для тестирования.

Содержит фикстуры для работы с тестовой базой данных, очистки таблиц
и создания тестового клиента FastAPI.
"""

import os
from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest
from fastapi import FastAPI
from httpx import ASGITransport
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool
from sqlalchemy.sql import text

from src.config.settings import get_database_settings
from src.database import get_async_session
from src.main import app
from src.models.base import Base


@pytest.fixture(scope="session")
async def test_engine(worker_id: str) -> AsyncGenerator[AsyncEngine, None]:
    """Создает асинхронный движок для тестовой базы данных.

    Для параллельного запуска тестов с pytest-xdist создает отдельную схему
    для каждого воркера на основе фикстуры worker_id.
    """
    settings = get_database_settings()

    # Определяем схему для текущего воркера
    if worker_id == "master":
        worker_id = "default"

    schema_name = f"test_{worker_id}"

    # Устанавливаем переменную окружения SCHEMA_NAME
    # для использования в миграциях и моделях
    os.environ["SCHEMA_NAME"] = schema_name

    # Устанавливаем схему в метаданных Base
    Base.metadata.schema = schema_name
    # Устанавливаем схему для всех таблиц в метаданных
    for table in Base.metadata.tables.values():
        table.schema = schema_name

    engine = create_async_engine(
        settings.database_url,
        echo=False,
        future=True,
        poolclass=NullPool,  # Не используем пул для тестов
    )

    # Создаем схему, если она не существует
    async with engine.begin() as conn:
        await conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}"))

    # Дропаем все таблицы в схеме
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        # Удаляем таблицу alembic_version, чтобы миграции применились заново
        await conn.execute(text(f"DROP TABLE IF EXISTS {schema_name}.alembic_version"))

    # Создаем таблицы по моделям (вместо миграций для тестов)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Закрываем движок после всех тестов
    await engine.dispose()


@pytest.fixture
async def test_session(test_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """Создает асинхронную сессию для тестов с автоматическим откатом изменений.

    Все изменения в тестах автоматически откатываются после завершения теста.
    Метод commit мокается для вызова flush без реального коммита в БД.
    """
    async_session_factory = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )

    session = async_session_factory()
    # Начинаем транзакцию, которая будет откачена после теста
    transaction = await session.begin()

    # Сохраняем оригинальные методы
    original_commit = session.commit
    original_flush = session.flush

    # Создаем мок для commit, который вызывает flush, но не выполняет реальный коммит
    async def mock_commit() -> None:
        """Мок коммита, который вызывает flush для синхронизации состояния."""
        await original_flush()
        # Реальный коммит не выполняется, транзакция будет откачена

    session.commit = mock_commit  # type: ignore[method-assign]
    # Оставляем flush как есть, так как он может использоваться
    # для синхронизации состояния

    try:
        yield session
    finally:
        # Восстанавливаем оригинальные методы перед откатом
        session.commit = original_commit  # type: ignore[method-assign]
        session.flush = original_flush  # type: ignore[method-assign]
        # Откатываем транзакцию, отменяя все изменения теста
        # Проверяем, активна ли ещё транзакция перед откатом
        if transaction.is_active:
            await transaction.rollback()
        # Закрываем сессию
        await session.close()


@pytest.fixture
async def test_session_no_mock(
    test_engine: AsyncEngine,
) -> AsyncGenerator[AsyncSession, None]:
    """Фикстура сессии без мока commit для диагностики проблем с event loop."""
    async_session_factory = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )

    session = async_session_factory()
    # Начинаем транзакцию, которая будет откачена после теста
    transaction = await session.begin()

    try:
        yield session
    finally:
        # Откатываем транзакцию, отменяя все изменения теста
        # Проверяем, активна ли ещё транзакция перед откатом
        if transaction.is_active:
            await transaction.rollback()
        await session.close()


@pytest.fixture
async def clean_tables(test_session: AsyncSession) -> AsyncGenerator[None, None]:
    """Очищает все таблицы в текущей схеме с помощью TRUNCATE.

    Фикстура должна использоваться в тестах, где требуется чистая база данных.
    Работает внутри транзакции теста, изменения автоматически откатываются.
    """
    # Получаем все таблицы в текущей схеме
    tables = Base.metadata.tables.values()

    if tables:
        # Формируем SQL для TRUNCATE всех таблиц с CASCADE
        table_names = ", ".join(
            [
                f"{table.schema}.{table.name}" if table.schema else table.name
                for table in tables
            ]
        )
        truncate_sql = text(f"TRUNCATE {table_names} CASCADE")

        # Выполняем TRUNCATE внутри текущей транзакции
        await test_session.execute(truncate_sql)
        # Не делаем commit, так как работаем внутри транзакции теста

    yield


@pytest.fixture
async def test_app(test_session: AsyncSession) -> AsyncGenerator[FastAPI, None]:
    """Возвращает основное приложение FastAPI
    с переопределенными зависимостями для тестов."""

    # Переопределяем зависимость для использования тестовой сессии
    async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
        yield test_session

    # Сохраняем оригинальное переопределение, если оно есть
    original_override = app.dependency_overrides.get(get_async_session)
    app.dependency_overrides[get_async_session] = override_get_async_session

    try:
        yield app
    finally:
        # Восстанавливаем оригинальное переопределение
        if original_override is not None:
            app.dependency_overrides[get_async_session] = original_override
        else:
            app.dependency_overrides.pop(get_async_session, None)


@pytest.fixture
async def test_client(test_app: FastAPI) -> AsyncGenerator[httpx.AsyncClient, None]:
    """Создает асинхронный тестовый клиент FastAPI."""
    transport = ASGITransport(app=test_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
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
