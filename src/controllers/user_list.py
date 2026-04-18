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

    async def __call__(
        self,
        session: AsyncSession,
        search: str | None = None,
    ) -> list[UserResponse]:
        """
        Основной метод контроллера, вызываемый из эндпоинта.

        :param session: Асинхронная сессия базы данных.
        :param search: Строка для поиска по email или username.
        :return: Список схем пользователей.
        """
        service = UserReadService(session)
        return await service(search)
