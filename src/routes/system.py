"""
Маршруты для системных операций мессенджера.

Содержит эндпоинты для проверки работоспособности системы,
мониторинга и других системных операций.
"""

from fastapi import APIRouter, status

router = APIRouter(prefix="/system", tags=["system"])


@router.get(
    "/ping",
    response_model=str,
    status_code=status.HTTP_200_OK,
    summary="Проверка доступности сервера",
    description="Возвращает 'pong' для подтверждения работоспособности сервера.",
    responses={
        200: {
            "description": "Сервер работает",
            "content": {"text/plain": {"example": "pong"}},
        }
    },
)
async def ping() -> str:
    """
    Проверка доступности сервера.

    Returns:
        str: Строка 'pong' для подтверждения работоспособности
    """
    return "pong"
