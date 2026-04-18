"""
Маршруты для операций с пользователями мессенджера.

Содержит эндпоинты для регистрации, авторизации и управления пользователями.
"""

from fastapi import APIRouter, status

from src.controllers.user_create import UserCreateController
from src.dependencies import ControllerType, DataBaseSession
from src.schemas.api.requests import UserCreate
from src.schemas.api.responses import UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/sign_up",
    response_model=UserResponse,
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
                        "uuid": "123e4567-e89b-12d3-a456-426614174000",
                    }
                }
            },
        }
    },
)
async def sign_up(
    user: UserCreate,
    session: DataBaseSession,
    controller: ControllerType[UserCreateController],
) -> UserResponse:
    """
    Регистрация нового пользователя.

    Args:
        user: Данные нового пользователя (email и пароль).
        session: Асинхронная сессия базы данных.
        controller: Контроллер для создания пользователей.

    Returns:
        Схема созданного пользователя.
    """
    return await controller(user, session)  # type: ignore[operator, no-any-return]
