"""
Модель пользователя для приложения мессенджера.

Содержит определение таблицы пользователей с базовыми полями:
uuid, email, password, а также унаследованные created_at и updated_at.
"""

import uuid
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel

if TYPE_CHECKING:
    from .session import Session


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

    sessions: Mapped[list["Session"]] = relationship(
        "Session",
        back_populates="user",
        lazy="select",
        cascade="all, delete-orphan",
    )
