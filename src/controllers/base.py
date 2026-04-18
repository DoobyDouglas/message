"""
Базовый контроллер для бизнес-логики приложения.

Предоставляет общий интерфейс для всех контроллеров.
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseController(ABC):
    """
    Абстрактный базовый контроллер.

    Все контроллеры должны наследоваться от этого класса
    и реализовывать метод __call__.
    """

    @abstractmethod
    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """
        Основной метод контроллера, вызываемый из эндпоинтов.

        :param args: Позиционные аргументы.
        :param kwargs: Именованные аргументы.
        :return: Результат выполнения бизнес-логики.
        """
        pass
