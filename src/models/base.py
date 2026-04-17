"""
Базовые модели SQLAlchemy для приложения мессенджера.

Содержит базовые классы для декларативного определения моделей,
автоматическое преобразование имен таблиц и общие поля (created_at, updated_at).
"""

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.orm.decl_api import declared_attr

from src.utils.string_utils import camel_to_snake


def snake_case_table(cls: Any) -> Any:
    """Декоратор для автоматического преобразования имени таблицы
    из CamelCase в snake_case.

    Если у класса уже задан __tablename__, он не изменяется.
    """
    if not hasattr(cls, "__tablename__"):
        cls.__tablename__ = camel_to_snake(cls.__name__)
    return cls


class Base(DeclarativeBase):
    """Базовый класс для всех декларативных моделей SQLAlchemy."""

    pass


class BaseModel(Base):
    """Абстрактная базовая модель с общими полями.

    Предоставляет поля created_at и updated_at для отслеживания времени
    создания и обновления записей, а также автоматическое преобразование
    имен таблиц из CamelCase в snake_case.
    """

    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """Автоматически генерирует имя таблицы в snake_case на основе имени класса.

        Returns:
            Имя таблицы в формате snake_case.
        """
        return camel_to_snake(cls.__name__)
