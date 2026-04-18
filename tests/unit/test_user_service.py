"""
Тесты для сервиса создания пользователей.

Содержит тесты для хэширования паролей и создания пользователей.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User
from src.schemas.api.requests import UserCreate
from src.services.user_service import CreateUserService
from src.utils.password import PasswordHasher


class TestCreateUserService:
    """Тесты для CreateUserService."""

    @pytest.mark.asyncio
    async def test_call_method(self) -> None:
        """Проверяет создание пользователя с хэшированием пароля через __call__."""
        mock_session = AsyncMock(spec=AsyncSession)
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        service = CreateUserService(session=mock_session)
        user_data = UserCreate(
            email="test@example.com",
            password="securepassword123",
        )

        # Мокируем PasswordHasher
        mock_password_hasher = MagicMock(spec=PasswordHasher)
        expected_hash = "mocked_hash"
        mock_password_hasher.hash_password.return_value = expected_hash
        service._password_hasher = mock_password_hasher

        result = await service(user_data)

        assert isinstance(result, User)
        assert result.email == user_data.email
        assert result.password == expected_hash
        # UUID может быть None до flush, проверяем что атрибут существует
        assert hasattr(result, "uuid")
        mock_session.add.assert_called_once_with(result)
        mock_session.commit.assert_awaited_once()
        mock_session.refresh.assert_awaited_once_with(result)
        mock_password_hasher.hash_password.assert_called_once_with(user_data.password)
