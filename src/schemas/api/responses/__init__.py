"""
Пакет схем ответов API.

Содержит схемы для исходящих данных (ответы).
"""

from .auth import AuthResponse
from .contact import ContactResponse
from .user import UserResponse

__all__ = ["UserResponse", "AuthResponse", "ContactResponse"]
