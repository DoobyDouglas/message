"""
Утилиты для работы с JWT токенами.

Содержит функции для создания, верификации и декодирования JWT токенов.
"""

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from jose import jwt
from jose.exceptions import JWTError

from src.config.settings import get_auth_settings


class JWTManager:
    """Менеджер JWT токенов.

    Предоставляет методы для создания, верификации и декодирования JWT токенов.
    """

    def __init__(self) -> None:
        """Инициализирует менеджер с настройками аутентификации."""
        self._settings = get_auth_settings()

    def create_access_token(
        self,
        *,
        user_uuid: UUID,
        session_uuid: UUID,
        expires_delta: timedelta | None = None,
    ) -> str:
        """Создает JWT токен доступа.

        Args:
            user_uuid: UUID пользователя.
            session_uuid: UUID сессии.
            expires_delta: Опциональное время жизни токена. Если не указано,
                используется значение из настроек.

        Returns:
            Закодированный JWT токен.
        """
        to_encode: dict[str, Any] = {
            "sub": str(user_uuid),
            "session": str(session_uuid),
            "type": "access",
        }
        if expires_delta:
            expire = datetime.now(UTC) + expires_delta
        else:
            expire = datetime.now(UTC) + timedelta(
                minutes=self._settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        to_encode.update({"exp": expire, "iat": datetime.now(UTC)})
        encoded_jwt = jwt.encode(
            to_encode,
            self._settings.JWT_SECRET,
            algorithm=self._settings.JWT_ALGORITHM,
        )
        return encoded_jwt

    def verify_token(self, token: str) -> dict[str, Any]:
        """Верифицирует JWT токен и возвращает полезную нагрузку.

        Args:
            token: JWT токен для верификации.

        Returns:
            Декодированная полезная нагрузка токена.

        Raises:
            jwt.JWTError: Если токен невалиден или истек.
        """
        try:
            payload = jwt.decode(
                token,
                self._settings.JWT_SECRET,
                algorithms=[self._settings.JWT_ALGORITHM],
            )
            return payload
        except JWTError:
            raise

    def decode_token(self, token: str) -> dict[str, Any]:
        """Декодирует JWT токен без верификации подписи.

        Внимание: Этот метод не проверяет подпись и срок действия токена.
        Используйте только для отладки или случаев, когда токен уже был верифицирован.

        Args:
            token: JWT токен для декодирования.

        Returns:
            Декодированная полезная нагрузка токена.
        """
        return jwt.get_unverified_claims(token)


# Создаём глобальный экземпляр для удобства использования
jwt_manager = JWTManager()

# Экспортируем удобные функции
create_access_token = jwt_manager.create_access_token
verify_token = jwt_manager.verify_token
decode_token = jwt_manager.decode_token
