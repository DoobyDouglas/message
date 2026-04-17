"""
Модуль тестирования системных эндпоинтов мессенджера.

Содержит тесты для проверки работоспособности основных API маршрутов.
"""

from fastapi.testclient import TestClient

from src.main import app


class TestSystem:
    client = TestClient(app)

    def test_ping(self) -> None:
        """
        Тестирование эндпоинта проверки доступности сервера.

        Проверяет:
        - Возвращает ли эндпоинт /system/ping статус код 200
        - Возвращает ли эндпоинт ожидаемый ответ 'pong'
        """
        response = self.client.get("/system/ping")
        assert response.status_code == 200
        assert response.json() == "pong"
