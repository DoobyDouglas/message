"""
Схемы ответов для работы с контактами.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ContactResponse(BaseModel):
    """
    Схема ответа с информацией о контакте.
    """

    uuid: UUID = Field(
        ...,
        description="UUID контакта",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
    )
    owner_id: UUID = Field(
        ...,
        description="UUID владельца контакта",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
    )
    contact_id: UUID = Field(
        ...,
        description="UUID пользователя, добавленного в контакты",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
    )
    created_at: datetime
    updated_at: datetime
