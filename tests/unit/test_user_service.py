"""
Тесты для сервиса создания пользователей.

Содержит тесты для хэширования паролей и создания пользователей.
"""

import pytest
from sqlalchemy import select

from src.models.user import User
from src.schemas.api.requests import UserCreate
from src.services.user_service import CreateUserService
from src.utils.password import PasswordHasher


class TestCreateUserService:
    """Тесты для CreateUserService."""

    @pytest.mark.asyncio
    async def test_call_method(self, test_session_no_mock) -> None:
        """Проверяет создание пользователя с хэшированием пароля через __call__."""
        service = CreateUserService(session=test_session_no_mock)
        user_data = UserCreate(
            email="test@example.com",
            password="securepassword123",
        )

        result = await service(user_data)

        # Проверяем, что возвращается объект User
        assert isinstance(result, User)
        assert result.email == user_data.email
        # Пароль должен быть хэширован (не равен исходному)
        assert result.password != user_data.password
        assert len(result.password) > 0
        # UUID должен быть сгенерирован
        assert result.uuid is not None

        # Проверяем, что пользователь сохранен в БД (можно найти по email)
        stmt = select(User).where(User.email == user_data.email)
        db_user = (await test_session_no_mock.scalars(stmt)).first()
        assert db_user is not None
        assert db_user.uuid == result.uuid
        assert db_user.password == result.password
        # Проверяем, что пароль действительно хэширован с помощью PasswordHasher
        password_hasher = PasswordHasher()
        assert password_hasher.verify_password(user_data.password, db_user.password)
