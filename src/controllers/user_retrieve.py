"""
Контроллер для получения конкретного пользователя.

Содержит бизнес-логику получения пользователя по UUID.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from src.controllers.base import BaseController
from src.schemas.api.responses.user import UserResponse
from src.services.user_read_service import UserReadService


class UserRetrieveController(BaseController):
    """
    Контроллер получения конкретного пользователя.
    """

    async def __call__(
        self,
        session: AsyncSession,
        user_uuid: uuid.UUID,
    ) -> UserResponse:
        """
        Основной метод контроллера, вызываемый из эндпоинта.

        :param session: Асинхронная сессия базы данных.
        :param user_uuid: UUID пользователя для получения.
        :return: Схема пользователя.
        """
        service = UserReadService(session)
        if (user := await service.get_user(user_uuid)) is None:
            from fastapi import HTTPException, status

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден",
            )
        return user
