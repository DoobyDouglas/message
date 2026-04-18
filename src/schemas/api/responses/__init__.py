"""
Пакет схем ответов API.

Содержит схемы для исходящих данных (ответы).
"""

from .auth import AuthResponse
from .user import UserResponse

__all__ = ["UserResponse", "AuthResponse"]
