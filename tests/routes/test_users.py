"""
Модуль тестирования эндпоинтов пользователей мессенджера.

Содержит тесты для регистрации, авторизации и управления пользователями.
"""

import pytest
from fastapi.testclient import TestClient

from src.main import app


class TestUsers:
    client = TestClient(app)

    def test_sign_up_valid(self) -> None:
        """
        Тестирование успешной регистрации пользователя.

        Проверяет:
        - Возвращает ли эндпоинт /users/sign_up статус код 200
        - Возвращает ли эндпоинт email и uuid
        - Не возвращает ли пароль
        """
        data = {
            "email": "newuser@example.com",
            "password": "securepassword123",
        }
        response = self.client.post("/users/sign_up", json=data)
        assert response.status_code == 200
        json_response = response.json()
        assert json_response["email"] == data["email"]
        assert "uuid" in json_response
        assert isinstance(json_response["uuid"], str)
        assert len(json_response["uuid"]) > 0
        assert "password" not in json_response

    @pytest.mark.parametrize(
        "data, expected_error_field",
        [
            (
                {"email": "invalid-email", "password": "securepassword123"},
                "email",
            ),
            (
                {"email": "user@example.com", "password": "short"},
                "password",
            ),
        ],
    )
    def test_sign_up_validation_errors(
        self, data: dict[str, str], expected_error_field: str
    ) -> None:
        """
        Тестирование регистрации с ошибками валидации полей.

        Проверяет:
        - Возвращает ли эндпоинт статус код 422 при невалидных данных
        - Содержит ли ответ ошибку для ожидаемого поля
        """
        response = self.client.post("/users/sign_up", json=data)
        assert response.status_code == 422
        json_response = response.json()
        assert expected_error_field in str(json_response).lower()

    @pytest.mark.parametrize(
        "data, expected_error_field",
        [
            (
                {"password": "securepassword123"},
                "email",
            ),
            (
                {"email": "user@example.com"},
                "password",
            ),
        ],
    )
    def test_sign_up_missing_fields(
        self, data: dict[str, str], expected_error_field: str
    ) -> None:
        """
        Тестирование регистрации с отсутствующими обязательными полями.

        Проверяет:
        - Возвращает ли эндпоинт статус код 422 при отсутствии обязательного поля
        - Содержит ли ответ ошибку для ожидаемого поля
        """
        response = self.client.post("/users/sign_up", json=data)
        assert response.status_code == 422
        json_response = response.json()
        assert expected_error_field in str(json_response).lower()
