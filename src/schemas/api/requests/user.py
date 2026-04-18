"""
Схемы запросов для операций с пользователями.

Содержит схемы для входящих данных (создание пользователя и т.д.).
"""

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """Схема для создания пользователя.

    Используется при регистрации нового пользователя.
    """

    email: EmailStr = Field(
        ...,
        description="Email пользователя",
        examples=["user@example.com"],
    )
    password: str = Field(
        ...,
        min_length=8,
        description="Пароль пользователя (минимум 8 символов)",
        examples=["securepassword123"],
    )
