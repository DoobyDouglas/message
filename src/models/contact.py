"""
Модель контакта для приложения мессенджера.

Содержит определение таблицы контактов, которая представляет собой связи между
пользователями: владелец контакта (owner) и пользователь, добавленный в контакты
(contact).
"""

import uuid
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel

if TYPE_CHECKING:
    from .user import User


class Contact(BaseModel):
    """Модель контакта.

    Хранит информацию о том, какой пользователь добавил другого пользователя в контакты.
    Владелец контакта (owner) может иметь множество контактов, каждый контакт — это
    другой пользователь системы.
    """

    __abstract__ = False

    uuid: Mapped[sa.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    owner_id: Mapped[sa.UUID] = mapped_column(
        UUID(as_uuid=True),
        sa.ForeignKey("user.uuid", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    contact_id: Mapped[sa.UUID] = mapped_column(
        UUID(as_uuid=True),
        sa.ForeignKey("user.uuid", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Отношение к владельцу контакта
    owner: Mapped["User"] = relationship(
        "User",
        foreign_keys=[owner_id],
        back_populates="contacts_owned",
        lazy="select",
    )
    # Отношение к пользователю, добавленному в контакты
    contact: Mapped["User"] = relationship(
        "User",
        foreign_keys=[contact_id],
        back_populates="contacts_added",
        lazy="select",
    )

    __table_args__ = (
        sa.UniqueConstraint("owner_id", "contact_id", name="uq_owner_contact"),
        sa.CheckConstraint("owner_id != contact_id", name="ck_owner_not_contact"),
    )
