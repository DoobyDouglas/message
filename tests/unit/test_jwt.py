"""
Тесты для утилит работы с JWT токенами.

Содержит тесты для создания, верификации и декодирования JWT токенов.
"""

from datetime import UTC, datetime, timedelta
from unittest.mock import patch
from uuid import UUID, uuid4

import pytest
from jose.exceptions import JWTError

from src.utils.jwt import JWTManager, create_access_token, decode_token, verify_token


class TestJWTManager:
    """Тесты для JWTManager."""

    @pytest.fixture
    def jwt_manager(self) -> JWTManager:
        """Фикстура для создания экземпляра JWTManager."""
        return JWTManager()

    @pytest.fixture
    def mock_settings(self) -> dict:
        """Фикстура с моком настроек аутентификации."""
        return {
            "JWT_SECRET": "test-secret-key",
            "JWT_ALGORITHM": "HS256",
            "ACCESS_TOKEN_EXPIRE_MINUTES": 30,
        }

    def test_create_access_token_default_expiry(
        self, jwt_manager: JWTManager, mock_settings: dict
    ) -> None:
        """Тестирует создание JWT токена с временем жизни по умолчанию."""
        user_uuid = uuid4()
        session_uuid = uuid4()

        with patch("src.utils.jwt.get_auth_settings") as mock_get_settings:
            mock_get_settings.return_value = type(
                "MockSettings",
                (),
                mock_settings,
            )()

            token = jwt_manager.create_access_token(
                user_uuid=user_uuid,
                session_uuid=session_uuid,
            )

        assert isinstance(token, str)
        assert len(token) > 0
        # Проверяем, что токен содержит три части (header.payload.signature)
        assert len(token.split(".")) == 3

    def test_create_access_token_custom_expiry(
        self, jwt_manager: JWTManager, mock_settings: dict
    ) -> None:
        """Тестирует создание JWT токена с кастомным временем жизни."""
        user_uuid = uuid4()
        session_uuid = uuid4()
        expires_delta = timedelta(minutes=15)

        with patch("src.utils.jwt.get_auth_settings") as mock_get_settings:
            mock_get_settings.return_value = type(
                "MockSettings",
                (),
                mock_settings,
            )()

            token = jwt_manager.create_access_token(
                user_uuid=user_uuid,
                session_uuid=session_uuid,
                expires_delta=expires_delta,
            )

        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_token_valid(
        self, jwt_manager: JWTManager, mock_settings: dict
    ) -> None:
        """Тестирует верификацию валидного JWT токена."""
        user_uuid = uuid4()
        session_uuid = uuid4()

        with patch("src.utils.jwt.get_auth_settings") as mock_get_settings:
            mock_get_settings.return_value = type(
                "MockSettings",
                (),
                mock_settings,
            )()

            token = jwt_manager.create_access_token(
                user_uuid=user_uuid,
                session_uuid=session_uuid,
            )
            payload = jwt_manager.verify_token(token)

        assert payload["sub"] == str(user_uuid)
        assert payload["session"] == str(session_uuid)
        assert payload["type"] == "access"
        assert "exp" in payload
        assert "iat" in payload
        assert isinstance(payload["exp"], int)
        assert isinstance(payload["iat"], int)

    def test_verify_token_invalid_secret(
        self, jwt_manager: JWTManager, mock_settings: dict
    ) -> None:
        """Тестирует верификацию токена с неверным секретом."""
        user_uuid = uuid4()
        session_uuid = uuid4()

        with patch("src.utils.jwt.get_auth_settings") as mock_get_settings:
            mock_get_settings.return_value = type(
                "MockSettings",
                (),
                mock_settings,
            )()

            token = jwt_manager.create_access_token(
                user_uuid=user_uuid,
                session_uuid=session_uuid,
            )

        # Меняем секрет для верификации
        with patch("src.utils.jwt.get_auth_settings") as mock_get_settings:
            mock_get_settings.return_value = type(
                "MockSettings",
                (),
                {"JWT_SECRET": "wrong-secret", "JWT_ALGORITHM": "HS256"},
            )()

            with pytest.raises(JWTError):
                jwt_manager.verify_token(token)

    def test_verify_token_expired(
        self, jwt_manager: JWTManager, mock_settings: dict
    ) -> None:
        """Тестирует верификацию истекшего токена."""
        user_uuid = uuid4()
        session_uuid = uuid4()

        with patch("src.utils.jwt.get_auth_settings") as mock_get_settings:
            mock_get_settings.return_value = type(
                "MockSettings",
                (),
                mock_settings,
            )()

            token = jwt_manager.create_access_token(
                user_uuid=user_uuid,
                session_uuid=session_uuid,
                expires_delta=timedelta(seconds=-1),  # Токен уже истек
            )

            with pytest.raises(JWTError):
                jwt_manager.verify_token(token)

    def test_decode_token_without_verification(
        self, jwt_manager: JWTManager, mock_settings: dict
    ) -> None:
        """Тестирует декодирование токена без верификации."""
        user_uuid = uuid4()
        session_uuid = uuid4()

        with patch("src.utils.jwt.get_auth_settings") as mock_get_settings:
            mock_get_settings.return_value = type(
                "MockSettings",
                (),
                mock_settings,
            )()

            token = jwt_manager.create_access_token(
                user_uuid=user_uuid,
                session_uuid=session_uuid,
            )
            payload = jwt_manager.decode_token(token)

        assert payload["sub"] == str(user_uuid)
        assert payload["session"] == str(session_uuid)
        assert payload["type"] == "access"

    def test_decode_token_malformed(self, jwt_manager: JWTManager) -> None:
        """Тестирует декодирование некорректного токена."""
        with pytest.raises(JWTError):
            jwt_manager.decode_token("malformed.token.here")


class TestJWTModuleFunctions:
    """Тесты для модульных функций JWT."""

    def test_create_access_token_function(self) -> None:
        """Тестирует функцию create_access_token."""
        user_uuid = uuid4()
        session_uuid = uuid4()

        with patch("src.utils.jwt.get_auth_settings") as mock_get_settings:
            mock_get_settings.return_value = type(
                "MockSettings",
                (),
                {
                    "JWT_SECRET": "test-secret",
                    "JWT_ALGORITHM": "HS256",
                    "ACCESS_TOKEN_EXPIRE_MINUTES": 30,
                },
            )()

            token = create_access_token(
                user_uuid=user_uuid,
                session_uuid=session_uuid,
            )

        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_token_function(self) -> None:
        """Тестирует функцию verify_token."""
        user_uuid = uuid4()
        session_uuid = uuid4()

        with patch("src.utils.jwt.get_auth_settings") as mock_get_settings:
            mock_get_settings.return_value = type(
                "MockSettings",
                (),
                {
                    "JWT_SECRET": "test-secret",
                    "JWT_ALGORITHM": "HS256",
                    "ACCESS_TOKEN_EXPIRE_MINUTES": 30,
                },
            )()

            token = create_access_token(
                user_uuid=user_uuid,
                session_uuid=session_uuid,
            )
            payload = verify_token(token)

        assert payload["sub"] == str(user_uuid)
        assert payload["session"] == str(session_uuid)

    def test_decode_token_function(self) -> None:
        """Тестирует функцию decode_token."""
        user_uuid = uuid4()
        session_uuid = uuid4()

        with patch("src.utils.jwt.get_auth_settings") as mock_get_settings:
            mock_get_settings.return_value = type(
                "MockSettings",
                (),
                {
                    "JWT_SECRET": "test-secret",
                    "JWT_ALGORITHM": "HS256",
                    "ACCESS_TOKEN_EXPIRE_MINUTES": 30,
                },
            )()

            token = create_access_token(
                user_uuid=user_uuid,
                session_uuid=session_uuid,
            )
            payload = decode_token(token)

        assert payload["sub"] == str(user_uuid)
        assert payload["session"] == str(session_uuid)