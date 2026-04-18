"""
Модуль тестирования эндпоинтов пользователей мессенджера.

Содержит тесты для регистрации, авторизации и управления пользователями.
"""

import httpx
import pytest


async def test_sign_up_valid(test_client: httpx.AsyncClient, unique_email: str) -> None:
    """
    Тестирование успешной регистрации пользователя.

    Проверяет:
    - Возвращает ли эндпоинт /users/sign_up статус код 200
    - Возвращает ли эндпоинт email и uuid
    - Не возвращает ли пароль
    """
    data = {
        "email": unique_email,
        "password": "securepassword123",
    }
    response = await test_client.post("/users/sign_up", json=data)
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
async def test_sign_up_validation_errors(
    test_client: httpx.AsyncClient,
    data: dict[str, str],
    expected_error_field: str,
) -> None:
    """
    Тестирование регистрации с ошибками валидации полей.

    Проверяет:
    - Возвращает ли эндпоинт статус код 422 при невалидных данных
    - Содержит ли ответ ошибку для ожидаемого поля
    """
    response = await test_client.post("/users/sign_up", json=data)
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
async def test_sign_up_missing_fields(
    test_client: httpx.AsyncClient,
    data: dict[str, str],
    expected_error_field: str,
) -> None:
    """
    Тестирование регистрации с отсутствующими обязательными полями.

    Проверяет:
    - Возвращает ли эндпоинт статус код 422 при отсутствии обязательного поля
    - Содержит ли ответ ошибку для ожидаемого поля
    """
    response = await test_client.post("/users/sign_up", json=data)
    assert response.status_code == 422
    json_response = response.json()
    assert expected_error_field in str(json_response).lower()


async def test_login_valid(test_client: httpx.AsyncClient, unique_email: str) -> None:
    """
    Тестирование успешного входа пользователя.

    Проверяет:
    - Возвращает ли эндпоинт /users/login статус код 200
    - Возвращает ли токен и данные пользователя
    - Устанавливается ли кука access_token
    """
    # Сначала создаем пользователя
    sign_up_data = {
        "email": unique_email,
        "password": "securepassword123",
    }
    sign_up_response = await test_client.post("/users/sign_up", json=sign_up_data)
    assert sign_up_response.status_code == 200

    # Пытаемся войти
    login_data = {
        "email": unique_email,
        "password": "securepassword123",
        "device_info": "Test Device",
    }
    response = await test_client.post("/users/login", json=login_data)
    assert response.status_code == 200
    json_response = response.json()

    # Проверяем структуру ответа
    assert "access_token" in json_response
    assert isinstance(json_response["access_token"], str)
    assert json_response["token_type"] == "bearer"
    assert "user" in json_response
    assert json_response["user"]["email"] == login_data["email"]
    assert "uuid" in json_response["user"]
    assert "session_id" in json_response
    assert "expires_in" in json_response

    # Проверяем, что установлена кука
    cookies = response.cookies
    assert "access_token" in cookies
    assert cookies["access_token"] == json_response["access_token"]


async def test_login_invalid_password(
    test_client: httpx.AsyncClient, unique_email: str
) -> None:
    """
    Тестирование входа с неверным паролем.

    Проверяет:
    - Возвращает ли эндпоинт статус код 401
    - Не устанавливается ли кука
    """
    # Создаем пользователя
    sign_up_data = {
        "email": unique_email,
        "password": "securepassword123",
    }
    sign_up_response = await test_client.post("/users/sign_up", json=sign_up_data)
    assert sign_up_response.status_code == 200

    # Пытаемся войти с неверным паролем
    login_data = {
        "email": unique_email,
        "password": "wrongpassword",
    }
    response = await test_client.post("/users/login", json=login_data)
    assert response.status_code == 401
    json_response = response.json()
    assert "detail" in json_response
    assert "Неверный email или пароль" in json_response["detail"]

    # Проверяем, что кука не установлена
    assert "access_token" not in response.cookies


async def test_login_user_not_found(
    test_client: httpx.AsyncClient, unique_email: str
) -> None:
    """
    Тестирование входа с несуществующим пользователем.

    Проверяет:
    - Возвращает ли эндпоинт статус код 401
    - Не устанавливается ли кука
    """
    login_data = {
        "email": unique_email,
        "password": "anypassword",
    }
    response = await test_client.post("/users/login", json=login_data)
    assert response.status_code == 401
    json_response = response.json()
    assert "detail" in json_response
    assert "Неверный email или пароль" in json_response["detail"]

    # Проверяем, что кука не установлена
    assert "access_token" not in response.cookies


async def test_login_without_device_info(
    test_client: httpx.AsyncClient, unique_email: str
) -> None:
    """
    Тестирование входа без информации об устройстве.

    Проверяет:
    - Работает ли вход без device_info
    - Устанавливается ли кука
    """
    # Создаем пользователя
    sign_up_data = {
        "email": unique_email,
        "password": "securepassword123",
    }
    sign_up_response = await test_client.post("/users/sign_up", json=sign_up_data)
    assert sign_up_response.status_code == 200

    # Пытаемся войти без device_info
    login_data = {
        "email": unique_email,
        "password": "securepassword123",
    }
    response = await test_client.post("/users/login", json=login_data)
    assert response.status_code == 200
    json_response = response.json()

    assert "access_token" in json_response
    assert "session_id" in json_response
    assert "access_token" in response.cookies
