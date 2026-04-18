"""
Утилиты для работы с паролями.

Содержит функции для безопасного хэширования и проверки паролей.
"""

import bcrypt


class PasswordHasher:
    """
    Класс для безопасного хэширования и проверки паролей.

    Использует bcrypt для генерации соли и хэширования паролей.
    """

    def hash_password(self, password: str) -> str:
        """
        Хэширует пароль с использованием bcrypt.

        Args:
            password: Пароль в виде строки.

        Returns:
            Хэшированный пароль в виде строки.
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    def verify_password(self, password: str, hashed: str) -> bool:
        """
        Проверяет пароль против хэша.

        Args:
            password: Пароль для проверки.
            hashed: Хэшированный пароль.

        Returns:
            True, если пароль совпадает, иначе False.
        """
        return bcrypt.checkpw(
            password.encode("utf-8"),
            hashed.encode("utf-8"),
        )
