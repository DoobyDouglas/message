"""
Тесты для схем пользователей.
"""

import pytest
from pydantic import ValidationError

from src.models.user import UserCreate


def test_user_create_valid() -> None:
    """Проверяет создание пользователя с валидными данными."""
    data = {
        "email": "user@example.com",
        "password": "securepassword123",
    }
    user = UserCreate(**data)
    assert user.email == data["email"]
    assert user.password == data["password"]


def test_user_create_email_validation() -> None:
    """Проверяет валидацию email."""
    # Некорректный email
    with pytest.raises(ValidationError) as exc_info:
        UserCreate(email="invalid-email", password="securepassword123")
    assert "email" in str(exc_info.value)

    # Корректный email проходит
    user = UserCreate(email="valid@example.com", password="securepassword123")
    assert user.email == "valid@example.com"


def test_user_create_password_min_length() -> None:
    """Проверяет минимальную длину пароля (8 символов)."""
    # Пароль короче 8 символов
    with pytest.raises(ValidationError) as exc_info:
        UserCreate(email="user@example.com", password="short")
    assert "password" in str(exc_info.value)

    # Пароль длиной 8 символов проходит
    user = UserCreate(email="user@example.com", password="eight123")
    assert user.password == "eight123"

    # Пароль длиннее 8 символов проходит
    user = UserCreate(email="user@example.com", password="verylongpassword123")
    assert user.password == "verylongpassword123"


def test_user_create_missing_fields() -> None:
    """Проверяет, что отсутствие обязательных полей вызывает ошибку."""
    # Отсутствует email
    with pytest.raises(ValidationError) as exc_info:
        UserCreate(**{"password": "securepassword123"})
    assert "email" in str(exc_info.value)

    # Отсутствует password
    with pytest.raises(ValidationError) as exc_info:
        UserCreate(**{"email": "user@example.com"})
    assert "password" in str(exc_info.value)
