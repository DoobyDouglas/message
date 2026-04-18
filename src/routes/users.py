"""
Маршруты для операций с пользователями мессенджера.

Содержит эндпоинты для регистрации, авторизации и управления пользователями.
"""

from fastapi import APIRouter, HTTPException, Query, Response, status

from src.config.settings import get_auth_settings
from src.controllers.auth_controller import AuthenticationController
from src.controllers.contact_create import ContactCreateController
from src.controllers.user_create import UserCreateController
from src.controllers.user_list import UserListController
from src.controllers.user_retrieve import UserRetrieveController
from src.dependencies import ControllerType, CurrentUserUUID, DataBaseSession
from src.schemas.api.requests import UserCreate, UserLogin
from src.schemas.api.responses import AuthResponse, ContactResponse, UserResponse
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
        "Возвращает список всех пользователей системы с возможностью "
        "поиска по email или username. Требуется аутентификация."
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
    search: str | None = Query(
        None, description="Поиск по email или username (регистронезависимо)"
    ),
) -> list[UserResponse]:
    """
    Получить список пользователей.

    :param user_uuid: UUID текущего пользователя (гарантирует аутентификацию).
    :param session: Асинхронная сессия базы данных.
    :param controller: Контроллер для получения списка пользователей.
    :param search: Строка для поиска по email или username.
    :return: Список схем пользователей.
    """
    return await controller(session=session, search=search)  # type: ignore[operator, no-any-return]


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить пользователя по ID",
    description=(
        "Возвращает информацию о конкретном пользователе по его UUID. "
        "Требуется аутентификация."
    ),
    responses={
        200: {
            "description": "Данные пользователя",
            "content": {
                "application/json": {
                    "example": {
                        "email": "user@example.com",
                        "username": "john_doe",
                        "uuid": "123e4567-e89b-12d3-a456-426614174000",
                    }
                }
            },
        },
        400: {
            "description": "Неверный формат UUID",
        },
        401: {
            "description": "Требуется аутентификация",
        },
        404: {
            "description": "Пользователь не найден",
        },
    },
)
async def get_user(
    user_id: str,
    user_uuid: CurrentUserUUID,
    session: DataBaseSession,
    controller: ControllerType[UserRetrieveController],
) -> UserResponse:
    """
    Получить пользователя по ID.

    :param user_id: UUID пользователя для получения (из пути запроса).
    :param user_uuid: UUID текущего аутентифицированного пользователя.
    :param session: Асинхронная сессия базы данных.
    :param controller: Контроллер для получения пользователя.
    :return: Схема пользователя.
    """
    from uuid import UUID

    try:
        target_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный формат UUID",
        )

    return await controller(session=session, user_uuid=target_uuid)  # type: ignore[operator, no-any-return]


@router.post(
    "/{user_id}/contact",
    response_model=ContactResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Добавить пользователя в контакты",
    description=(
        "Добавляет указанного пользователя (user_id из пути) в контакты "
        "текущего пользователя. Требуется аутентификация. "
        "Пользователь не может добавить себя в контакты."
    ),
    responses={
        201: {
            "description": "Контакт успешно создан",
            "content": {
                "application/json": {
                    "example": {
                        "uuid": "123e4567-e89b-12d3-a456-426614174000",
                        "owner_id": "123e4567-e89b-12d3-a456-426614174000",
                        "contact_id": "123e4567-e89b-12d3-a456-426614174001",
                        "created_at": "2026-04-18T20:34:59.123456+03:00",
                        "updated_at": "2026-04-18T20:34:59.123456+03:00",
                    }
                }
            },
        },
        400: {
            "description": "Некорректные данные (неверный формат UUID)",
        },
        401: {
            "description": "Требуется аутентификация",
        },
        404: {
            "description": "Пользователь не найден",
        },
        409: {
            "description": "Контакт уже существует или попытка добавить себя",
        },
    },
)
async def add_contact(
    user_id: str,
    user_uuid: CurrentUserUUID,
    session: DataBaseSession,
    controller: ControllerType[ContactCreateController],
) -> ContactResponse:
    """
    Добавить пользователя в контакты.

    :param user_id: UUID пользователя, которого добавляем в контакты
        (из пути запроса).
    :param user_uuid: UUID текущего аутентифицированного пользователя
        (владельца контакта).
    :param session: Асинхронная сессия базы данных.
    :param controller: Контроллер для добавления контактов.
    :return: Схема созданного контакта.
    """
    from uuid import UUID

    try:
        contact_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный формат UUID",
        )

    return await controller(contact_uuid, user_uuid, session)  # type: ignore[operator, no-any-return]
