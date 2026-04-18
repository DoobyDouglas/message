"""
Контроллер для получения списка пользователей.

Содержит бизнес-логику получения списка пользователей.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from src.controllers.base import BaseController
from src.schemas.api.responses.user import UserResponse
from src.services.user_read_service import UserReadService


class UserListController(BaseController):
    """
    Контроллер получения списка пользователей.
    """

    async def __list(self, session: AsyncSession) -> list[UserResponse]:
        """
        Получает список пользователей.

        Args:
            session: Асинхронная сессия базы данных.

        Returns:
            Список схем пользователей.
        """
        service = UserReadService(session)
        return await service()

    async def __call__(self, session: AsyncSession) -> list[UserResponse]:
        """
        Основной метод контроллера, вызываемый из эндпоинта.

        Args:
            session: Асинхронная сессия базы данных.

        Returns:
            Список схем пользователей.
        """
        return await self.__list(session)
