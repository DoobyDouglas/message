"""
Тесты для сервиса аутентификации пользователей.

Содержит тесты для проверки пароля, создания сессий и генерации JWT токенов.
"""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User
from src.schemas.api.requests.auth import UserLogin
from src.services.auth_service import (
    AuthenticationService,
    InvalidPasswordError,
    UserNotFoundError,
)
from src.utils.password import PasswordHasher


class TestAuthenticationService:
    """Тесты для AuthenticationService."""

    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        """Фикстура для мока асинхронной сессии БД."""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def mock_password_hasher(self) -> MagicMock:
        """Фикстура для мока PasswordHasher."""
        hasher = MagicMock(spec=PasswordHasher)
        hasher.verify_password = MagicMock(return_value=True)
        return hasher

    @pytest.fixture
    def mock_settings(self) -> dict:
        """Фикстура с моком настроек аутентификации."""
        return {
            "SESSION_EXPIRE_DAYS": 30,
            "ACCESS_TOKEN_EXPIRE_MINUTES": 30,
        }

    @pytest.fixture
    def sample_user(self) -> User:
        """Фикстура для создания тестового пользователя."""
        user_uuid = uuid4()
        user = User(
            uuid=user_uuid,
            email="test@example.com",
            password="hashed_password",
        )
        return user

    @pytest.fixture
    def valid_login_data(self) -> UserLogin:
        """Фикстура для создания валидных данных для входа."""
        return UserLogin(
            email="test@example.com",
            password="plain_password",
            device_info="Test Device",
        )

    @pytest.mark.asyncio
    async def test_authentication_success(
        self,
        mock_session: AsyncMock,
        mock_password_hasher: MagicMock,
        mock_settings: dict,
        sample_user: User,
        valid_login_data: UserLogin,
    ) -> None:
        """Тестирует успешную аутентификацию пользователя."""
        # Мокаем запрос к БД
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_session.execute.return_value = mock_result

        # Мокаем создание сессии
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        service = AuthenticationService(session=mock_session)
        service._password_hasher = mock_password_hasher

        with patch("src.services.auth_service.get_auth_settings") as mock_get_settings:
            mock_get_settings.return_value = type(
                "MockSettings",
                (),
                mock_settings,
            )()

            with patch(
                "src.services.auth_service.create_access_token"
            ) as mock_create_token:
                expected_token = "test.jwt.token"
                mock_create_token.return_value = expected_token

                result = await service(valid_login_data)

        # Проверяем, что пользователь был найден
        mock_session.execute.assert_called_once()
        # Проверяем, что пароль был проверен
        mock_password_hasher.verify_password.assert_called_once_with(
            valid_login_data.password, sample_user.password
        )
        # Проверяем, что сессия была создана
        mock_session.add.assert_called_once()
        mock_session.commit.assert_awaited_once()
        mock_session.refresh.assert_awaited_once()
        # Проверяем, что токен был сгенерирован
        mock_create_token.assert_called_once()
        # Проверяем результат
        assert result.access_token == expected_token
        assert result.token_type == "bearer"
        assert result.user.email == sample_user.email
        assert result.user.uuid == str(sample_user.uuid)
        assert result.session_id is not None
        assert result.expires_in == mock_settings["ACCESS_TOKEN_EXPIRE_MINUTES"] * 60

    @pytest.mark.asyncio
    async def test_authentication_user_not_found(
        self,
        mock_session: AsyncMock,
        mock_password_hasher: MagicMock,
        valid_login_data: UserLogin,
    ) -> None:
        """Тестирует аутентификацию с несуществующим пользователем."""
        # Мокаем запрос к БД - пользователь не найден
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        service = AuthenticationService(session=mock_session)
        service._password_hasher = mock_password_hasher

        with pytest.raises(UserNotFoundError) as exc_info:
            await service(valid_login_data)

        assert str(valid_login_data.email) in str(exc_info.value)
        mock_session.execute.assert_called_once()
        mock_password_hasher.verify_password.assert_not_called()

    @pytest.mark.asyncio
    async def test_authentication_invalid_password(
        self,
        mock_session: AsyncMock,
        mock_password_hasher: MagicMock,
        sample_user: User,
        valid_login_data: UserLogin,
    ) -> None:
        """Тестирует аутентификацию с неверным паролем."""
        # Мокаем запрос к БД - пользователь найден
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_session.execute.return_value = mock_result
        # Мокаем проверку пароля - возвращает False
        mock_password_hasher.verify_password.return_value = False

        service = AuthenticationService(session=mock_session)
        service._password_hasher = mock_password_hasher

        with pytest.raises(InvalidPasswordError) as exc_info:
            await service(valid_login_data)

        assert "Неверный пароль" in str(exc_info.value)
        mock_session.execute.assert_called_once()
        mock_password_hasher.verify_password.assert_called_once_with(
            valid_login_data.password, sample_user.password
        )

    @pytest.mark.asyncio
    async def test_create_session_with_device_info(
        self,
        mock_session: AsyncMock,
        mock_settings: dict,
        sample_user: User,
    ) -> None:
        """Тестирует создание сессии с информацией об устройстве."""
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        service = AuthenticationService(session=mock_session)

        with patch("src.services.auth_service.get_auth_settings") as mock_get_settings:
            mock_get_settings.return_value = type(
                "MockSettings",
                (),
                mock_settings,
            )()

            with patch("src.services.auth_service.datetime") as mock_datetime:
                fixed_time = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
                mock_datetime.now.return_value = fixed_time

                session = await service._create_session(sample_user, "Test Device")

        # Проверяем, что сессия создана с правильными данными
        assert session.user_uuid == sample_user.uuid
        assert session.device_info == "Test Device"
        expected_expires_at = fixed_time + timedelta(
            days=mock_settings["SESSION_EXPIRE_DAYS"]
        )
        assert session.expires_at == expected_expires_at
        mock_session.add.assert_called_once_with(session)
        mock_session.commit.assert_awaited_once()
        mock_session.refresh.assert_awaited_once_with(session)

    @pytest.mark.asyncio
    async def test_create_session_without_device_info(
        self,
        mock_session: AsyncMock,
        mock_settings: dict,
        sample_user: User,
    ) -> None:
        """Тестирует создание сессии без информации об устройстве."""
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        service = AuthenticationService(session=mock_session)

        with patch("src.services.auth_service.get_auth_settings") as mock_get_settings:
            mock_get_settings.return_value = type(
                "MockSettings",
                (),
                mock_settings,
            )()

            session = await service._create_session(sample_user, None)

        assert session.user_uuid == sample_user.uuid
        assert session.device_info is None
        mock_session.add.assert_called_once_with(session)  # type: ignore[unreachable]
        mock_session.commit.assert_awaited_once()
        mock_session.refresh.assert_awaited_once_with(session)
