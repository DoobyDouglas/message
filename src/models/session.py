"""
Модель сессии пользователя для приложения мессенджера.

Содержит определение таблицы сессий с полями:
uuid сессии, uuid пользователя (внешний ключ), дата сгорания сессии,
информация об устройстве пользователя.
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel

if TYPE_CHECKING:
    from .user import User


class Session(BaseModel):
    """Модель сессии пользователя.

    Хранит информацию о активных сессиях пользователей: уникальный идентификатор,
    ссылка на пользователя, дата истечения сессии и информация об устройстве.
    """

    __abstract__ = False

    uuid: Mapped[UUID] = mapped_column(  # type: ignore[type-arg, unused-ignore]
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    user_uuid: Mapped[UUID] = mapped_column(  # type: ignore[type-arg, unused-ignore]
        UUID(as_uuid=True),
        sa.ForeignKey("user.uuid", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    expires_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
    )
    device_info: Mapped[str] = mapped_column(
        sa.String(500),
        nullable=True,
        default=None,
    )

    user: Mapped["User"] = relationship("User", back_populates="sessions")
