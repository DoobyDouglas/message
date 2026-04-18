"""
Схемы запросов для операций аутентификации.

Содержит схемы для входящих данных (логин и т.д.).
"""

from pydantic import BaseModel, EmailStr, Field


class UserLogin(BaseModel):
    """Схема для входа пользователя.

    Используется при аутентификации пользователя.
    """

    email: EmailStr = Field(
        ...,
        description="Email пользователя",
        examples=["user@example.com"],
    )
    password: str = Field(
        ...,
        description="Пароль пользователя",
        examples=["securepassword123"],
    )
    device_info: str | None = Field(
        None,
        description="Информация об устройстве пользователя (опционально)",
        examples=["Chrome on Windows 10"],
    )
