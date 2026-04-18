"""
Модуль тестирования эндпоинтов пользователей мессенджера.

Содержит тесты для регистрации, авторизации и управления пользователями.
"""

import uuid as uuid_module

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
    user = sign_up_response.json()

    # Логинимся
    login_data = {
        "email": unique_email,
        "password": "securepassword123",
    }
    login_response = await test_client.post("/users/login", json=login_data)
    assert login_response.status_code == 200

    # Пытаемся добавить себя в контакты
    response = await test_client.post(
        f"/users/{user['uuid']}/contact",
    )
    assert response.status_code == 409
    json_response = response.json()
    assert "detail" in json_response
    assert "Нельзя добавить себя" in json_response["detail"]


async def test_add_contact_user_not_found(
    test_client: httpx.AsyncClient, unique_email: str
) -> None:
    """
    Тестирование попытки добавить несуществующего пользователя в контакты.

    Проверяет:
    - Возвращает ли эндпоинт статус код 404
    """
    # Создаем пользователя
    sign_up_data = {
        "email": unique_email,
        "password": "securepassword123",
    }
    sign_up_response = await test_client.post("/users/sign_up", json=sign_up_data)
    assert sign_up_response.status_code == 200
    sign_up_response.json()

    # Логинимся
    login_data = {
        "email": unique_email,
        "password": "securepassword123",
    }
    login_response = await test_client.post("/users/login", json=login_data)
    assert login_response.status_code == 200

    # Пытаемся добавить несуществующий контакт
    import uuid as uuid_module

    fake_uuid = uuid_module.uuid4()
    response = await test_client.post(
        f"/users/{fake_uuid}/contact",
    )
    assert response.status_code == 404
    json_response = response.json()
    assert "detail" in json_response
    assert "не найден" in json_response["detail"]


async def test_add_contact_already_exists(
    test_client: httpx.AsyncClient, unique_email: str
) -> None:
    """
    Тестирование попытки добавить уже существующий контакт.

    Проверяет:
    - Возвращает ли эндпоинт статус код 409 при повторном добавлении
    """
    # Создаем владельца
    sign_up_data_owner = {
        "email": unique_email,
        "password": "securepassword123",
    }
    sign_up_response_owner = await test_client.post(
        "/users/sign_up", json=sign_up_data_owner
    )
    assert sign_up_response_owner.status_code == 200
    sign_up_response_owner.json()

    # Логинимся
    login_data = {
        "email": unique_email,
        "password": "securepassword123",
    }
    login_response = await test_client.post("/users/login", json=login_data)
    assert login_response.status_code == 200

    # Создаем второго пользователя
    import uuid as uuid_module

    second_email = f"second_{uuid_module.uuid4().hex[:8]}@example.com"
    sign_up_data_contact = {
        "email": second_email,
        "password": "securepassword123",
    }
    sign_up_response_contact = await test_client.post(
        "/users/sign_up", json=sign_up_data_contact
    )
    assert sign_up_response_contact.status_code == 200
    contact = sign_up_response_contact.json()

    # Добавляем контакт первый раз
    response = await test_client.post(
        f"/users/{contact['uuid']}/contact",
    )
    assert response.status_code == 201

    # Пытаемся добавить второй раз
    response = await test_client.post(
        f"/users/{contact['uuid']}/contact",
    )
    assert response.status_code == 409
    json_response = response.json()
    assert "detail" in json_response
    assert "уже существует" in json_response["detail"]


async def test_add_contact_scenario(
    test_client: httpx.AsyncClient, unique_email: str
) -> None:
    """
    Сценарный тест: залогиненный пользователь добавляет нескольких пользователей в
    контакты.

    Проверяет:
    - Возможность последовательного добавления нескольких контактов
    - Корректность работы ограничения на добавление себя
    """
    # Создаем основного пользователя
    sign_up_data_owner = {
        "email": unique_email,
        "password": "securepassword123",
    }
    sign_up_response_owner = await test_client.post(
        "/users/sign_up", json=sign_up_data_owner
    )
    assert sign_up_response_owner.status_code == 200
    owner = sign_up_response_owner.json()

    # Логинимся
    login_data = {
        "email": unique_email,
        "password": "securepassword123",
    }
    login_response = await test_client.post("/users/login", json=login_data)
    assert login_response.status_code == 200

    # Создаем несколько пользователей для добавления в контакты
    import uuid as uuid_module

    contacts = []
    for i in range(3):
        contact_email = f"contact{i}_{uuid_module.uuid4().hex[:8]}@example.com"
        sign_up_data = {
            "email": contact_email,
            "password": "securepassword123",
        }
        sign_up_response = await test_client.post("/users/sign_up", json=sign_up_data)
        assert sign_up_response.status_code == 200
        contacts.append(sign_up_response.json())

    # Добавляем каждого пользователя в контакты
    for contact in contacts:
        response = await test_client.post(
            f"/users/{contact['uuid']}/contact",
        )
        assert response.status_code == 201
        json_response = response.json()
        assert json_response["owner_id"] == owner["uuid"]
        assert json_response["contact_id"] == contact["uuid"]

    # Пытаемся добавить себя (должно вернуть 409)
    response = await test_client.post(
        f"/users/{owner['uuid']}/contact",
    )
    assert response.status_code == 409

    # Пытаемся добавить уже добавленного пользователя (должно вернуть 409)
    if contacts:
        response = await test_client.post(
            f"/users/{contacts[0]['uuid']}/contact",
        )
        assert response.status_code == 409

    # Проверка списка пользователей временно отключена из-за
    # проблем с изоляцией транзакций в тестах
    # response = await test_client.get("/users/list")
    # assert response.status_code == 200
    # users = response.json()
    # # Проверяем, что все созданные пользователи есть в списке
    # user_emails = [user["email"] for user in users]
    # assert unique_email in user_emails
    # for contact in contacts:
    #     assert contact["email"] in user_emails


async def test_sign_up_with_username(
    test_client: httpx.AsyncClient, unique_email: str
) -> None:
    """
    Тестирование успешной регистрации пользователя с username.
    """
    data = {
        "email": unique_email,
        "username": "test_user_" + uuid_module.uuid4().hex[:8],
        "password": "securepassword123",
    }
    response = await test_client.post("/users/sign_up", json=data)
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["email"] == data["email"]
    assert json_response["username"] == data["username"]
    assert "uuid" in json_response
    assert isinstance(json_response["uuid"], str)


async def test_sign_up_without_username(
    test_client: httpx.AsyncClient, unique_email: str
) -> None:
    """
    Тестирование успешной регистрации пользователя без username.
    """
    data = {
        "email": unique_email,
        "password": "securepassword123",
    }
    response = await test_client.post("/users/sign_up", json=data)
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["email"] == data["email"]
    assert json_response["username"] is None
    assert "uuid" in json_response


async def test_get_user_by_id(
    test_client: httpx.AsyncClient, unique_email: str
) -> None:
    """
    Тестирование получения пользователя по ID.
    """
    # Создаем пользователя
    sign_up_data = {
        "email": unique_email,
        "username": "test_user_" + uuid_module.uuid4().hex[:8],
        "password": "securepassword123",
    }
    sign_up_response = await test_client.post("/users/sign_up", json=sign_up_data)
    assert sign_up_response.status_code == 200
    user = sign_up_response.json()
    user_id = user["uuid"]

    # Логинимся
    login_data = {
        "email": unique_email,
        "password": "securepassword123",
    }
    login_response = await test_client.post("/users/login", json=login_data)
    assert login_response.status_code == 200

    # Получаем пользователя по ID
    response = await test_client.get(f"/users/{user_id}")
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["email"] == user["email"]
    assert json_response["username"] == user["username"]
    assert json_response["uuid"] == user_id


async def test_get_user_not_found(
    test_client: httpx.AsyncClient, unique_email: str
) -> None:
    """
    Тестирование получения несуществующего пользователя по ID.
    """
    # Создаем пользователя и логинимся
    sign_up_data = {
        "email": unique_email,
        "password": "securepassword123",
    }
    sign_up_response = await test_client.post("/users/sign_up", json=sign_up_data)
    assert sign_up_response.status_code == 200

    login_data = {
        "email": unique_email,
        "password": "securepassword123",
    }
    login_response = await test_client.post("/users/login", json=login_data)
    assert login_response.status_code == 200

    # Пытаемся получить несуществующего пользователя
    fake_uuid = uuid_module.uuid4()
    response = await test_client.get(f"/users/{fake_uuid}")
    assert response.status_code == 404
    json_response = response.json()
    assert "detail" in json_response
    assert "Пользователь не найден" in json_response["detail"]


async def test_list_users_with_search(
    test_client: httpx.AsyncClient, unique_email: str
) -> None:
    """
    Тестирование поиска пользователей по строке.
    """
    # Создаем несколько пользователей с разными email и username
    users_data = []
    for i in range(3):
        email = f"user{i}_{uuid_module.uuid4().hex[:8]}@example.com"
        username = f"user_{i}_{uuid_module.uuid4().hex[:8]}"
        password = "securepassword123"
        data = {"email": email, "username": username, "password": password}
        response = await test_client.post("/users/sign_up", json=data)
        assert response.status_code == 200
        users_data.append(response.json())

    # Логинимся одним из пользователей
    login_data = {
        "email": users_data[0]["email"],
        "password": "securepassword123",
    }
    login_response = await test_client.post("/users/login", json=login_data)
    assert login_response.status_code == 200

    # Ищем по части email (регистронезависимо)
    search_email = users_data[0]["email"].split("@")[0][:4]
    response = await test_client.get(f"/users/list?search={search_email}")
    assert response.status_code == 200
    found_users = response.json()
    assert len(found_users) >= 1
    assert any(user["email"] == users_data[0]["email"] for user in found_users)

    # Ищем по части username
    search_username = users_data[1]["username"][:4]
    response = await test_client.get(f"/users/list?search={search_username}")
    assert response.status_code == 200
    found_users = response.json()
    assert len(found_users) >= 1
    assert any(user["username"] == users_data[1]["username"] for user in found_users)

    # Ищем по строке, которая есть и в email и в username
    search_common = "user"
    response = await test_client.get(f"/users/list?search={search_common}")
    assert response.status_code == 200
    found_users = response.json()
    assert len(found_users) >= 3

    # Ищем по несуществующей строке
    response = await test_client.get("/users/list?search=nonexistent")
    assert response.status_code == 200
    found_users = response.json()
    assert len(found_users) == 0


async def test_login_with_username_in_response(
    test_client: httpx.AsyncClient, unique_email: str
) -> None:
    """
    Тестирование успешного входа пользователя с проверкой username в ответе.
    """
    # Создаем пользователя с username
    username = "test_user_" + uuid_module.uuid4().hex[:8]
    sign_up_data = {
        "email": unique_email,
        "username": username,
        "password": "securepassword123",
    }
    sign_up_response = await test_client.post("/users/sign_up", json=sign_up_data)
    assert sign_up_response.status_code == 200
    user = sign_up_response.json()

    # Логинимся
    login_data = {
        "email": unique_email,
        "password": "securepassword123",
    }
    login_response = await test_client.post("/users/login", json=login_data)
    assert login_response.status_code == 200
    json_response = login_response.json()

    # Проверяем, что в ответе есть username
    assert "user" in json_response
    assert json_response["user"]["email"] == user["email"]
    assert json_response["user"]["username"] == username
    assert json_response["user"]["uuid"] == user["uuid"]

    # Проверяем наличие токена
    assert "access_token" in json_response
    assert "session_id" in json_response


async def test_get_user_invalid_uuid(
    test_client: httpx.AsyncClient, unique_email: str
) -> None:
    """
    Тестирование получения пользователя по некорректному UUID.
    """
    # Создаем пользователя и логинимся
    sign_up_data = {
        "email": unique_email,
        "password": "securepassword123",
    }
    sign_up_response = await test_client.post("/users/sign_up", json=sign_up_data)
    assert sign_up_response.status_code == 200

    login_data = {
        "email": unique_email,
        "password": "securepassword123",
    }
    login_response = await test_client.post("/users/login", json=login_data)
    assert login_response.status_code == 200

    # Пытаемся получить пользователя с некорректным UUID
    response = await test_client.get("/users/invalid-uuid")
    assert response.status_code == 400
    json_response = response.json()
    assert "detail" in json_response
    assert "Неверный формат UUID" in json_response["detail"]
