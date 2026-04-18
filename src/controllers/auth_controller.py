"""
Контроллер аутентификации пользователей.

Содержит бизнес-логику управления аутентификацией.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from src.controllers.base import BaseController
from src.schemas.api.requests.auth import UserLogin
from src.schemas.api.responses.auth import AuthResponse
from src.services.auth_service import AuthenticationService


class AuthenticationControllerError(Exception):
    """Базовое исключение контроллера аутентификации."""

    pass


class AuthenticationController(BaseController):
    """
    Контроллер аутентификации пользователей.
    """

    async def __authenticate(
        self, login_data: UserLogin, session: AsyncSession
    ) -> AuthResponse:
        """
        Выполняет аутентификацию пользователя.

        Args:
            login_data: Данные для входа (email, password, device_info).
            session: Асинхронная сессия базы данных.

        Returns:
            Ответ аутентификации с токеном и данными пользователя.

        Raises:
            UserNotFoundError: Если пользователь не найден.
            InvalidPasswordError: Если пароль неверный.
        """
        service = AuthenticationService(session)
        return await service(login_data)

    async def __call__(
        self, login_data: UserLogin, session: AsyncSession
    ) -> AuthResponse:
        """
        Основной метод контроллера, вызываемый из эндпоинта.

        Args:
            login_data: Данные для входа (email, password, device_info).
            session: Асинхронная сессия базы данных.

        Returns:
            Ответ аутентификации с токеном и данными пользователя.

        Raises:
            UserNotFoundError: Если пользователь не найден.
            InvalidPasswordError: Если пароль неверный.
        """
        return await self.__authenticate(login_data, session)
