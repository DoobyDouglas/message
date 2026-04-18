"""
Контроллер для добавления контактов.

Содержит логику обработки запроса на добавление пользователя в контакты.
"""

from uuid import UUID

from fastapi import HTTPException, status

from src.controllers.base import BaseController
from src.dependencies import CurrentUserUUID, DataBaseSession
from src.schemas.api.responses.contact import ContactResponse
from src.services.contact_service import ContactService


class ContactCreateController(BaseController):
    """
    Контроллер для добавления контактов.

    Обрабатывает запрос на добавление пользователя в контакты текущего пользователя.
    """

    async def __call__(
        self,
        contact_id: UUID,
        current_user_uuid: CurrentUserUUID,
        session: DataBaseSession,
    ) -> ContactResponse:
        """
        Добавляет пользователя в контакты текущего пользователя.

        :param contact_id: UUID пользователя, которого добавляем в контакты
            (из пути запроса).
        :param current_user_uuid: UUID текущего аутентифицированного пользователя
            (владельца контакта).
        :param session: Асинхронная сессия базы данных.
        :return: Схема созданного контакта.
        :raise: HTTPException 404: Если пользователь не найден.
        :raise: HTTPException 409: Если контакт уже существует.
        :raise: HTTPException 400: При других ошибках валидации.
        """
        # Создаём сервис и выполняем операцию
        service = ContactService(session=session)
        try:
            contact = await service(
                owner_id=current_user_uuid,
                contact_id=contact_id,
            )
        except ValueError as e:
            error_message = str(e)
            if "не найден" in error_message:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=error_message,
                )
            if (
                "уже существует" in error_message
                or "Нельзя добавить себя" in error_message
            ):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=error_message,
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_message,
            )

        return contact
