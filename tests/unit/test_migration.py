"""
Тесты для модуля миграций базы данных.
"""

from unittest.mock import patch

import pytest

from src.utils.migration import get_alembic_config, run_migrations, run_migrations_sync


def test_get_alembic_config() -> None:
    """Проверяет создание конфигурации Alembic."""
    config = get_alembic_config()

    assert config.get_main_option("script_location") == "migrations"
    assert config.get_main_option("sqlalchemy.url") is not None


@pytest.mark.asyncio
async def test_run_migrations_success() -> None:
    """Проверяет успешное выполнение миграций."""
    with patch("src.utils.migration.command.upgrade") as mock_upgrade:
        # Запускаем миграции
        await run_migrations()

        # Проверяем, что функция upgrade была вызвана
        mock_upgrade.assert_called_once()
        args = mock_upgrade.call_args
        assert args[0][1] == "head"  # revision


@pytest.mark.asyncio
async def test_run_migrations_exception() -> None:
    """Проверяет обработку исключения при выполнении миграций."""
    with patch(
        "src.utils.migration.command.upgrade", side_effect=Exception("Migration error")
    ):
        # Ожидаем исключение
        with pytest.raises(Exception, match="Migration error"):
            await run_migrations()


def test_run_migrations_sync_success() -> None:
    """Проверяет успешное выполнение синхронных миграций."""
    with patch("src.utils.migration.command.upgrade") as mock_upgrade:
        run_migrations_sync()

        mock_upgrade.assert_called_once()
        args = mock_upgrade.call_args
        assert args[0][1] == "head"  # revision


def test_run_migrations_sync_exception() -> None:
    """Проверяет обработку исключения при выполнении синхронных миграций."""
    with patch(
        "src.utils.migration.command.upgrade",
        side_effect=Exception("Sync migration error"),
    ):
        with pytest.raises(Exception, match="Sync migration error"):
            run_migrations_sync()
