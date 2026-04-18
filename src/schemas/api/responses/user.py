"""
Схемы ответов для операций с пользователями.

Содержит схемы для исходящих данных (ответы API).
"""

from pydantic import BaseModel, EmailStr, Field


class UserResponse(BaseModel):
    """Схема для ответа с данными пользователя.

    Используется при возвращении данных пользователя без пароля.
    """

    email: EmailStr = Field(
        ...,
        description="Email пользователя",
        examples=["user@example.com"],
    )
    username: str | None = Field(
        None,
        description="Имя пользователя (опционально)",
        examples=["john_doe"],
    )
    uuid: str = Field(
        ...,
        description="Уникальный идентификатор пользователя",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
    )
