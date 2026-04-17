"""
Модели данных для приложения мессенджера.

Содержит определения таблиц базы данных и базовые классы для ORM.
"""

from .base import Base, BaseModel, snake_case_table
from .user import User

__all__ = ["Base", "BaseModel", "snake_case_table", "User"]
