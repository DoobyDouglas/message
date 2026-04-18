"""
Контроллер для создания пользователей.

Содержит бизнес-логику регистрации новых пользователей.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from src.controllers.base import BaseController
from src.schemas.api.requests import UserCreate
from src.schemas.api.responses import UserResponse
from src.services.user_service import CreateUserService


class UserCreateController(BaseController):
    """
    Контроллер создания пользователей.
    """

    async def __create(
        self,
        user: UserCreate,
        session: AsyncSession,
    ) -> UserResponse:
        """
        Создает нового пользователя.

        :param user: Данные нового пользователя.
        :param session: Асинхронная сессия базы данных.
        :return: Схема созданного пользователя.
        """
        service = CreateUserService(session)
        created_user = await service(user)
        return UserResponse(
            email=created_user.email,
            username=created_user.username,
            uuid=str(created_user.uuid),
        )

    async def __call__(
        self,
        user: UserCreate,
        session: AsyncSession,
    ) -> UserResponse:
        """
        Основной метод контроллера, вызываемый из эндпоинта.

        :param user: Данные нового пользователя.
        :param session: Асинхронная сессия базы данных.
        :return: Схема созданного пользователя.
        """
        return await self.__create(user, session)
