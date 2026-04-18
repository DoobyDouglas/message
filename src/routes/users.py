"""
Маршруты для операций с пользователями мессенджера.

Содержит эндпоинты для регистрации, авторизации и управления пользователями.
"""

from fastapi import APIRouter, HTTPException, Response, status

from src.config.settings import get_auth_settings
from src.controllers.auth_controller import AuthenticationController
from src.controllers.user_create import UserCreateController
from src.controllers.user_list import UserListController
from src.dependencies import ControllerType, CurrentUserUUID, DataBaseSession
from src.schemas.api.requests import UserCreate, UserLogin
from src.schemas.api.responses import AuthResponse, UserResponse
from src.services.auth_service import InvalidPasswordError, UserNotFoundError

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


@router.post(
    "/login",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
    summary="Вход пользователя в систему",
    description="Аутентифицирует пользователя и возвращает JWT токен.",
    responses={
        200: {
            "description": "Успешная аутентификация",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer",
                        "user": {
                            "email": "user@example.com",
                            "uuid": "123e4567-e89b-12d3-a456-426614174000",
                        },
                        "session_id": "123e4567-e89b-12d3-a456-426614174000",
                        "expires_in": 1800,
                    }
                }
            },
        },
        401: {
            "description": "Неверный email или пароль",
        },
    },
)
async def login(
    user: UserLogin,
    response: Response,
    session: DataBaseSession,
    controller: ControllerType[AuthenticationController],
) -> AuthResponse:
    """
    Вход пользователя в систему.

    Args:
        user: Данные для входа (email, пароль, опционально информация об устройстве).
        response: Объект ответа для установки куки.
        session: Асинхронная сессия базы данных.
        controller: Контроллер аутентификации.

    Returns:
        Ответ аутентификации с токеном и данными пользователя.

    Raises:
        HTTPException: Если email или пароль неверны (код 401).
    """
    try:
        auth_result = await controller(user, session)  # type: ignore[operator]
    except (UserNotFoundError, InvalidPasswordError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
        )

    # Получаем настройки аутентификации
    auth_settings = get_auth_settings()

    # Устанавливаем куку с JWT токеном
    response.set_cookie(
        key="access_token",
        value=auth_result.access_token,
        httponly=auth_settings.COOKIE_HTTPONLY,
        max_age=auth_result.expires_in,
        secure=auth_settings.COOKIE_SECURE,
        samesite=auth_settings.COOKIE_SAMESITE,
    )

    return auth_result  # type: ignore[no-any-return]


@router.get(
    "/list",
    response_model=list[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="Получить список пользователей",
    description=(
        "Возвращает список всех пользователей системы. Требуется аутентификация."
    ),
    responses={
        200: {
            "description": "Список пользователей",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "email": "user1@example.com",
                            "uuid": "123e4567-e89b-12d3-a456-426614174000",
                        },
                        {
                            "email": "user2@example.com",
                            "uuid": "123e4567-e89b-12d3-a456-426614174001",
                        },
                    ]
                }
            },
        },
        401: {
            "description": "Требуется аутентификация",
        },
    },
)
async def list_users(
    user_uuid: CurrentUserUUID,
    session: DataBaseSession,
    controller: ControllerType[UserListController],
) -> list[UserResponse]:
    """
    Получить список пользователей.

    :param user_uuid: UUID текущего пользователя (гарантирует аутентификацию).
    :param session: Асинхронная сессия базы данных.
    :param controller: Контроллер для получения списка пользователей.
    :return: Список схем пользователей.
    """
    return await controller(session)  # type: ignore[operator, no-any-return]
