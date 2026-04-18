"""
Пакет зависимостей для FastAPI приложения.

Содержит общие зависимости, используемые в роутах приложения.
"""

from typing import Annotated, Any, TypeVar, cast
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.services.user_service import CreateUserService
from src.utils.jwt import verify_token

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


async def get_user_service(session: DataBaseSession) -> CreateUserService:
    """
    Зависимость для получения сервиса создания пользователей.

    :param session: Асинхронная сессия базы данных.
    :return: Экземпляр CreateUserService с переданной сессией.
    """
    return CreateUserService(session)


UserServiceDep = Annotated[CreateUserService, Depends(get_user_service)]


def extract_token_from_request(request: Request) -> str | None:
    """
    Извлекает JWT токен из запроса.

    Проверяет куку 'access_token', затем заголовок Authorization (Bearer token).

    :param request: Запрос FastAPI.
    :return: JWT токен или None, если токен не найден.
    """
    # Проверяем куку
    token: str | None = request.cookies.get("access_token")
    if token:
        return token

    # Проверяем заголовок Authorization
    auth_header: str | None = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header[7:]  # Убираем префикс "Bearer "

    return None


async def get_current_session_payload(request: Request) -> dict[str, Any]:
    """
    Зависимость для получения данных текущей сессии из JWT токена.

    :param request: Запрос FastAPI.
    :return: Полезная нагрузка JWT токена с полями 'sub' (user_uuid) и
        'session' (session_uuid).
    :raise: HTTPException: Если токен отсутствует, невалиден или истек (код 401).
    """
    token: str | None = extract_token_from_request(request)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен аутентификации отсутствует",
        )

    try:
        payload: dict[str, Any] = verify_token(token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный или истекший токен",
        )

    # Проверяем наличие обязательных полей
    if "sub" not in payload or "session" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен не содержит необходимых данных",
        )

    return payload


async def get_current_user_uuid(
    payload: dict[str, Any] = Depends(get_current_session_payload),
) -> UUID:
    """
    Зависимость для получения UUID текущего пользователя.

    :param payload: Полезная нагрузка JWT токена.
    :return: UUID текущего пользователя.
    """
    return UUID(payload["sub"])


async def get_current_session_uuid(
    payload: dict[str, Any] = Depends(get_current_session_payload),
) -> UUID:
    """
    Зависимость для получения UUID текущей сессии.

    :param payload: Полезная нагрузка JWT токена.
    :return: UUID текущей сессии.
    """
    return UUID(payload["session"])


# Аннотированные типы для использования в эндпоинтах
CurrentSessionPayload = Annotated[dict[str, Any], Depends(get_current_session_payload)]
CurrentUserUUID = Annotated[UUID, Depends(get_current_user_uuid)]
CurrentSessionUUID = Annotated[UUID, Depends(get_current_session_uuid)]
