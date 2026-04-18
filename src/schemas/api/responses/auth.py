"""
Схемы ответов для операций аутентификации.

Содержит схемы для исходящих данных (ответы API).
"""

from pydantic import BaseModel, Field

from .user import UserResponse


class AuthResponse(BaseModel):
    """Схема для ответа аутентификации.

    Содержит токены и информацию о пользователе.
    """

    access_token: str = Field(
        ...,
        description="JWT токен доступа",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."],
    )
    token_type: str = Field(
        "bearer",
        description="Тип токена",
        examples=["bearer"],
    )
    user: UserResponse = Field(
        ...,
        description="Данные пользователя",
    )
    session_id: str = Field(
        ...,
        description="Уникальный идентификатор сессии",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
    )
    expires_in: int = Field(
        ...,
        description="Время жизни токена в секундах",
        examples=[1800],
    )
