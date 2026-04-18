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

        :param password: Пароль в виде строки.
        :return: Хэшированный пароль в виде строки.
        """
        salt: bytes = bcrypt.gensalt()
        hashed: bytes = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    def verify_password(self, password: str, hashed: str) -> bool:
        """
        Проверяет пароль против хэша.

        :param password: Пароль для проверки.
        :param hashed: Хэшированный пароль.
        :return: True, если пароль совпадает, иначе False.
        """
        return bcrypt.checkpw(
            password.encode("utf-8"),
            hashed.encode("utf-8"),
        )
