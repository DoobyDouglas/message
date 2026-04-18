"""
Сервис аутентификации пользователей.

Содержит бизнес-логику аутентификации пользователей,
создания сессий и генерации JWT токенов.
"""

from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.settings import get_auth_settings
from src.models.session import Session
from src.models.user import User
from src.schemas.api.requests.auth import UserLogin
from src.schemas.api.responses.auth import AuthResponse
from src.schemas.api.responses.user import UserResponse
from src.services.base import BaseService
from src.utils.jwt import create_access_token
from src.utils.password import PasswordHasher


class AuthenticationError(Exception):
    """Базовое исключение для ошибок аутентификации."""

    pass


class UserNotFoundError(AuthenticationError):
    """Исключение, когда пользователь не найден."""

    pass


class InvalidPasswordError(AuthenticationError):
    """Исключение, когда пароль неверный."""

    pass


class AuthenticationService(BaseService):
    """
    Сервис для аутентификации пользователей.

    Обеспечивает проверку пароля, создание сессии и генерацию JWT токена.
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        Инициализирует сервис с сессией базы данных.

        Args:
            session: Асинхронная сессия базы данных.
        """
        self._session = session
        self._password_hasher = PasswordHasher()
        self._settings = get_auth_settings()

    async def _get_user_by_email(self, email: str) -> User:
        """
        Находит пользователя по email.

        Args:
            email: Email пользователя.

        Returns:
            ORM модель пользователя.

        Raises:
            UserNotFoundError: Если пользователь не найден.
        """
        stmt = select(User).where(User.email == email)
        result = await self._session.execute(stmt)
        user = result.scalar_one_or_none()
        if user is None:
            raise UserNotFoundError(f"Пользователь с email {email} не найден")
        return user

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Проверяет пароль.

        Args:
            plain_password: Пароль в открытом виде.
            hashed_password: Хэшированный пароль.

        Returns:
            True, если пароль верный, иначе False.
        """
        return self._password_hasher.verify_password(plain_password, hashed_password)

    async def _create_session(
        self, user: User, device_info: str | None = None
    ) -> Session:
        """
        Создает новую сессию для пользователя.

        Args:
            user: Пользователь, для которого создается сессия.
            device_info: Информация об устройстве (опционально).

        Returns:
            Созданная ORM модель сессии.
        """
        expires_at = datetime.now(UTC) + timedelta(
            days=self._settings.SESSION_EXPIRE_DAYS
        )
        session = Session(
            user_uuid=user.uuid,
            expires_at=expires_at,
            device_info=device_info,
        )
        self._session.add(session)
        await self._session.commit()
        await self._session.refresh(session)
        return session

    async def __call__(self, login_data: UserLogin) -> AuthResponse:
        """
        Выполняет аутентификацию пользователя.

        Args:
            login_data: Данные для входа (email, password, device_info).

        Returns:
            Ответ аутентификации с токеном и данными пользователя.

        Raises:
            UserNotFoundError: Если пользователь не найден.
            InvalidPasswordError: Если пароль неверный.
        """
        # Находим пользователя
        user = await self._get_user_by_email(login_data.email)

        # Проверяем пароль
        if not self._verify_password(login_data.password, user.password):
            raise InvalidPasswordError("Неверный пароль")

        # Создаем сессию
        session = await self._create_session(user, login_data.device_info)

        # Генерируем JWT токен
        access_token = create_access_token(
            user_uuid=user.uuid,  # type: ignore[arg-type]
            session_uuid=session.uuid,  # type: ignore[arg-type]
        )

        # Создаем ответ
        user_response = UserResponse(
            email=user.email,
            uuid=str(user.uuid),
        )

        return AuthResponse(
            access_token=access_token,
            token_type="bearer",
            user=user_response,
            session_id=str(session.uuid),
            expires_in=self._settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
