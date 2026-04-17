"""
Маршруты для операций с пользователями мессенджера.

Содержит эндпоинты для регистрации, авторизации и управления пользователями.
"""

from fastapi import APIRouter, status

from src.dependencies import DataBaseSession
from src.models.user import UserCreate

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/sign_up",
    response_model=UserCreate,
    status_code=status.HTTP_200_OK,
    summary="Регистрация нового пользователя",
    description="Создает нового пользователя в системе.",
    responses={
        200: {
            "description": "Пользователь успешно создан",
            "content": {
                "application/json": {
                    "example": {
                        "email": "user@example.com",
                        "password": "securepassword123"
                    }
                }
            },
        }
    },
)
async def sign_up(
    user: UserCreate,
    session: DataBaseSession,
) -> UserCreate:
    """
    Регистрация нового пользователя.

    Args:
        user: Данные нового пользователя (email и пароль).
        session: Асинхронная сессия базы данных.

    Returns:
        Схема созданного пользователя (пока моковый ответ).
    """
    _ = session  # Заглушка для линтера
    return user
