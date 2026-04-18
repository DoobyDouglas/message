"""
Пакет схем запросов API.

Содержит схемы для входящих данных (запросы).
"""

from .auth import UserLogin
from .user import UserCreate

__all__ = ["UserCreate", "UserLogin"]
