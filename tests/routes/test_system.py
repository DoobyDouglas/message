"""
Модуль тестирования системных эндпоинтов мессенджера.

Содержит тесты для проверки работоспособности основных API маршрутов.
"""

import httpx


async def test_ping(test_client: httpx.AsyncClient) -> None:
    """
    Тестирование эндпоинта проверки доступности сервера.

    Проверяет:
    - Возвращает ли эндпоинт /system/ping статус код 200
    - Возвращает ли эндпоинт ожидаемый ответ 'pong'
    """
    response = await test_client.get("/system/ping")
    assert response.status_code == 200
    assert response.json() == "pong"
