"""
Пакет зависимостей для FastAPI приложения.

Содержит общие зависимости, используемые в роутах приложения.
"""

from typing import Annotated, TypeVar, cast

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session

DataBaseSession = Annotated[AsyncSession, Depends(get_async_session)]

ControllerTypeVar = TypeVar("ControllerTypeVar")


class ControllerType[ControllerTypeVar]:
    """
    Generic тип для внедрения контроллеров в эндпоинты FastAPI.
    """

    @classmethod
    def __class_getitem__(cls, controller_cls: type[ControllerTypeVar]) -> type:
        """
        Возвращает аннотированный тип для внедрения зависимости контроллера.
        """
        def get_controller() -> ControllerTypeVar:
            return controller_cls()

        # Используем cast чтобы mypy принял Annotated как type
        return cast(type, Annotated[controller_cls, Depends(get_controller)])
