"""
Сервис для чтения пользователей.

Содержит бизнес-логику получения пользователей из базы данных.
"""

import uuid

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User
from src.schemas.api.responses.user import UserResponse
from src.services.base import BaseService


class UserReadService(BaseService):
    """
    Сервис для чтения пользователей.

    Обеспечивает получение пользователей из базы данных.
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        Инициализирует сервис с сессией базы данных.

        :param session: Асинхронная сессия базы данных.
        """
        self._session = session

    async def __call__(self, search: str | None = None) -> list[UserResponse]:
        """
        Получает список всех пользователей с возможностью поиска.

        :param search: Строка для поиска по email или username (регистронезависимо).
        :return: Список схем пользователей.
        """
        query = select(User)
        if search:
            search_pattern = f"%{search}%"
            query = query.where(
                or_(
                    User.email.ilike(search_pattern),
                    User.username.ilike(search_pattern),
                )
            )
        users = await self._session.scalars(query)
        return [
            UserResponse(
                email=user.email,
                username=user.username,
                uuid=str(user.uuid),
            )
            for user in users
        ]

    async def get_user(self, user_uuid: uuid.UUID) -> UserResponse | None:
        """
        Получает пользователя по UUID.

        :param user_uuid: UUID пользователя.
        :return: Схема пользователя или None, если пользователь не найден.
        """
        query = select(User).where(User.uuid == user_uuid)
        user = await self._session.scalar(query)
        if user is None:
            return None
        return UserResponse(
            email=user.email,
            username=user.username,
            uuid=str(user.uuid),
        )
