"""
Модель пользователя для приложения мессенджера.

Содержит определение таблицы пользователей с базовыми полями:
uuid, email, password, а также унаследованные created_at и updated_at.
"""

import uuid

import sqlalchemy as sa
from pydantic import BaseModel as PydanticBaseModel
from pydantic import EmailStr, Field
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseModel


class User(BaseModel):
    """Модель пользователя.

    Хранит информацию о пользователях системы: уникальный идентификатор,
    email для входа и хэшированный пароль.
    """

    __abstract__ = False

    uuid: Mapped[sa.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    email: Mapped[str] = mapped_column(
        sa.String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    password: Mapped[str] = mapped_column(
        sa.String(255),
        nullable=False,
    )


class UserCreate(PydanticBaseModel):
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
