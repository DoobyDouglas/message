"""
Сервис для работы с контактами.

Содержит бизнес-логику добавления пользователей в контакты.
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.contact import Contact
from src.models.user import User
from src.schemas.api.responses.contact import ContactResponse
from src.services.base import BaseService


class ContactService(BaseService):
    """
    Сервис для работы с контактами.

    Обеспечивает добавление пользователей в контакты.
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        Инициализирует сервис с сессией базы данных.

        :param session: Асинхронная сессия базы данных.
        """
        self._session = session

    async def __call__(self, owner_id: UUID, contact_id: UUID) -> ContactResponse:
        """
        Добавляет пользователя в контакты.

        :param owner_id: UUID владельца контакта.
        :param contact_id: UUID пользователя, которого добавляют в контакты.
        :return: Схема созданного контакта.
        :raise: ValueError: Если пользователь не найден или попытка добавить себя.
        :raise: IntegrityError: Если контакт уже существует.
        """
        # Проверяем, что owner_id и contact_id не совпадают
        if owner_id == contact_id:
            raise ValueError("Нельзя добавить себя в контакты")

        # Проверяем существование пользователя-владельца
        owner_query = select(User).where(User.uuid == owner_id)
        owner_result = await self._session.scalars(owner_query)
        owner = owner_result.first()
        if not owner:
            raise ValueError(f"Пользователь с UUID {owner_id} не найден")

        # Проверяем существование добавляемого пользователя
        contact_query = select(User).where(User.uuid == contact_id)
        contact_result = await self._session.scalars(contact_query)
        contact = contact_result.first()
        if not contact:
            raise ValueError(f"Пользователь с UUID {contact_id} не найден")

        # Создаём запись контакта
        new_contact = Contact(owner_id=owner_id, contact_id=contact_id)
        self._session.add(new_contact)

        try:
            await self._session.commit()
            await self._session.refresh(new_contact)
        except IntegrityError as e:
            await self._session.rollback()
            # Проверяем, является ли ошибка нарушением уникальности
            if "uq_owner_contact" in str(e):
                raise ValueError("Контакт уже существует")
            raise

        return ContactResponse(
            uuid=new_contact.uuid,  # type: ignore[arg-type]
            owner_id=new_contact.owner_id,  # type: ignore[arg-type]
            contact_id=new_contact.contact_id,  # type: ignore[arg-type]
            created_at=new_contact.created_at,
            updated_at=new_contact.updated_at,
        )
