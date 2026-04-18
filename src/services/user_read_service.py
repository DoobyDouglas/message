"""
Сервис для чтения пользователей.

Содержит бизнес-логику получения пользователей из базы данных.
"""

from sqlalchemy import select
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

        Args:
            session: Асинхронная сессия базы данных.
        """
        self._session = session

    async def __call__(self) -> list[UserResponse]:
        """
        Получает список всех пользователей.

        Returns:
            Список схем пользователей.
        """
        stmt = select(User)
        result = await self._session.execute(stmt)
        users = result.scalars().all()
        return [
            UserResponse(
                email=user.email,
                uuid=str(user.uuid),
            )
            for user in users
        ]
