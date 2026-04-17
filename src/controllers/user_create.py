"""
Контроллер для создания пользователей.

Содержит бизнес-логику регистрации новых пользователей.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from src.controllers.base import BaseController
from src.models.user import UserCreate


class UserCreateController(BaseController):
    """
    Контроллер создания пользователей.
    """

    async def __create(self, user: UserCreate, session: AsyncSession) -> UserCreate:  # noqa: F841
        """
        Создает нового пользователя.

        Args:
            user: Данные нового пользователя.
            session: Асинхронная сессия базы данных.

        Returns:
            Схема созданного пользователя (заглушка).
        """
        return user

    async def __call__(self, user: UserCreate, session: AsyncSession) -> UserCreate:
        """
        Основной метод контроллера, вызываемый из эндпоинта.

        Args:
            user: Данные нового пользователя.
            session: Асинхронная сессия базы данных.

        Returns:
            Схема созданного пользователя.
        """
        return await self.__create(user, session)
