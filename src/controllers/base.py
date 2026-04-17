"""
Базовый контроллер для обработчиков запросов.

Содержит абстрактный класс BaseController, который принимает зависимость
DataBaseSession в конструкторе и требует реализации метода call у наследников.
"""

from abc import ABC, abstractmethod
from typing import Any

from src.dependencies import DataBaseSession


class BaseController(ABC):
    """Абстрактный базовый контроллер для обработчиков запросов.

    Наследники должны реализовать метод call, который выполняет основную логику
    обработки запроса. Конструктор принимает зависимость DataBaseSession для
    работы с базой данных.
    """

    def __init__(self, session: DataBaseSession) -> None:
        """Инициализирует контроллер с сессией базы данных.

        Args:
            session: Асинхронная сессия базы данных (зависимость FastAPI).
        """
        self._session = session

    @abstractmethod
    async def call(self, *args: Any, **kwargs: Any) -> Any:
        """Абстрактный метод выполнения логики контроллера.

        Args:
            *args: Позиционные аргументы.
            **kwargs: Именованные аргументы.

        Returns:
            Результат выполнения контроллера.
        """
        raise NotImplementedError("Метод call должен быть реализован в наследнике")
