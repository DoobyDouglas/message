"""
Сервис для создания пользователей.

Содержит бизнес-логику создания пользователей с хэшированием паролей.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User
from src.schemas.api.requests import UserCreate
from src.services.base import BaseService
from src.utils.password import PasswordHasher


class CreateUserService(BaseService):
    """
    Сервис для создания пользователей.

    Обеспечивает создание пользователей с хэшированием паролей.
    Использует PasswordHasher для безопасного хэширования.
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        Инициализирует сервис с сессией базы данных.

        Args:
            session: Асинхронная сессия базы данных.
        """
        self._session = session
        self._password_hasher = PasswordHasher()

    def __hash_password(self, password: str) -> str:
        """
        Хэширует пароль с использованием PasswordHasher.

        Args:
            password: Пароль в виде строки.

        Returns:
            Хэшированный пароль в виде строки.
        """
        return self._password_hasher.hash_password(password)

    async def __call__(self, user_data: UserCreate) -> User:
        """
        Создает нового пользователя с хэшированным паролем.

        Args:
            user_data: Данные нового пользователя.

        Returns:
            Созданная ORM модель пользователя.
        """
        hashed_password = self.__hash_password(user_data.password)
        user = User(
            email=user_data.email,
            password=hashed_password,
        )
        self._session.add(user)
        await self._session.commit()
        await self._session.refresh(user)
        return user
