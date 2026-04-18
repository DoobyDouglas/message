"""
Пакет схем запросов API.

Содержит схемы для входящих данных (запросы).
"""

from .auth import UserLogin
from .contact import ContactCreateRequest
from .user import UserCreate

__all__ = ["UserCreate", "UserLogin", "ContactCreateRequest"]
