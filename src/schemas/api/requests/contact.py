"""
Схемы запросов для работы с контактами.
"""

from uuid import UUID

from pydantic import BaseModel, Field


class ContactCreateRequest(BaseModel):
    """
    Схема запроса на добавление контакта.

    Содержит идентификатор пользователя, которого нужно добавить в контакты.
    """

    contact_id: UUID = Field(
        ...,
        description="UUID пользователя, которого добавляют в контакты",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
    )
