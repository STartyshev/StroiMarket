# tests.jwt_authorization_test.py
import pytest
import pytest_asyncio
from unittest.mock import MagicMock, AsyncMock
from fastapi.testclient import TestClient

from api.security.authentication import create_hashed_password, create_jwt_token
from database.actions import check_login_availability
from database.models import User
from api.errors.authentication.exceptions import UnavailableLogin
from api.schemas.authentication import RegistrationCredentials
from main import market_app


# Имитация метода refresh асинхронной сессии
async def mock_refresh(user):
    user.id = 1
    user.role = "user"

# Имитация зависимости, которая проверяет свободен ли логин
async def mock_check_login_availability(credentials: RegistrationCredentials):
    # Предположим логин newTestUser2 уже занят
    if credentials.login == "newTestUser2":
        raise UnavailableLogin()
    else:
        return True

# Имитация функции поиска пользователя в БД по логину
# async_session - фиктивный параметр для соответствия реальной функции
async def mock_get_user_by_login_from_db(login: str, async_session):
    # Предположим пользователь с логином newTestUser есть в БД
    if login == "newTestUser":
        # Возвращаем пользователя из БД
        return User(id=7, login=login, hashed_password=create_hashed_password("newTestUserPassword1"), role="user")
    else:
        # Остальных пользователей в БД нет
        return None

@pytest.mark.asyncio
class TestAuthorization:
    @pytest_asyncio.fixture(scope="session")
    async def test_client(self):
        with TestClient(market_app) as client:
            yield client

    # Вызывается перед каждым тестом
    @pytest.fixture(autouse=True)
    def setup(self, test_client):
        self.test_client = test_client
        # Запомнили изначальные зависимости
        self.original_dependencies = market_app.dependency_overrides.copy()
        # Поменяли зависимость в которой используется подключение к БД
        market_app.dependency_overrides[check_login_availability] = mock_check_login_availability

    @pytest.fixture(autouse=True)
    def mock_async_session_maker_(self, mocker):
        self.mock_async_session = MagicMock()
        # "async_session.add(new_user)", async_session.add(new_user) - ничего не возвращает
        self.mock_async_session.add.return_value = None
        # "await async_session.commit()", async_session.commit() - возвращает корутину
        self.mock_async_session.commit = AsyncMock()
        # "await async_session.refresh(new_user)", await async_session.refresh(new_user) - возвращает корутину
        # и изменяет объект new_user
        self.mock_async_session.refresh = AsyncMock(side_effect=mock_refresh)

        mock_async_session_maker = mocker.patch("api.endpoints.jwt_auth.async_session_maker")
        # "async with async_session_maker() as async_session:"
        # async_session_maker() возвращает объект класса AsyncSession - асинхронный контекстный менеджер,
        # который вызывает метод __aenter__, который создает объект асинхронной сессии с БД,
        # который присваивается в async_session
        # Соответствующий мок:
        mock_async_session_maker.return_value.__aenter__.return_value = self.mock_async_session
        # Вызывается при закрытии асинхронного контекста
        mock_async_session_maker.return_value.__aexit__.return_value = None

        return mock_async_session_maker

    @pytest.fixture(autouse=True)
    def mock_get_user_by_login_from_db_(self, mocker):
        mock_function = mocker.patch("api.endpoints.jwt_auth.get_user_by_login_from_db")
        mock_function.side_effect = mock_get_user_by_login_from_db

        return mock_function

    # Обращение к конечной точке регистрации с корректными данными
    async def test_registration_correct_data(self):
        response = self.test_client.post(
            "http://127.0.0.1:8000/registration_jwt",
            data={
                "login": "newTestUser",
                "password": "newTestUser1"
            })

        assert response.status_code == 200
        assert response.json() == {
            "id": 1,
            "role": "user"
        }
        assert response.cookies["jwt_access_token"] is not None

    # Обращение к конечной точке регистрации с недопустимым символом в логине
    async def test_registration_invalid_characters_login(self):
        response = self.test_client.post(
            "http://127.0.0.1:8000/registration_jwt",
            data={
                "login": "newTestUser*",
                "password": "newTestUser1"
            })

        assert response.status_code == 422
        assert response.json()["message"] == "Логин содержит недопустимые символы."
        assert ("jwt_access_token" in response.cookies) is False

    # Обращение к конечной точке регистрации с недопустимой длиной логина
    async def test_registration_invalid_length_login(self):
        response = self.test_client.post(
            "http://127.0.0.1:8000/registration_jwt",
            data={
                "login": "TU",
                "password": "newTestUser1"
            })

        assert response.status_code == 422
        assert response.json()["message"] == "Поле \"Логин\" должно иметь длину от 3 до 32 символов включительно."
        assert ("jwt_access_token" in response.cookies) is False

    # Обращение к конечной точке регистрации с недопустимым языковым форматом логина
    async def test_registration_invalid_language_format_login(self):
        response = self.test_client.post(
            "http://127.0.0.1:8000/registration_jwt",
            data={
                "login": "НовыйЛогин",
                "password": "newTestUser1"
            })

        assert response.status_code == 422
        assert response.json()["message"] == "Логин должен содержать символы только латинского алфавита."
        assert ("jwt_access_token" in response.cookies) is False

    # Обращение к конечной точке регистрации с неприемлемой сложностью пароля
    # Тесты на запрещенные знаки, длину и языковой формат пароля опустим,
    # так как это те же самые функции, которые используются в проверке логина
    async def test_registration_unacceptable_password_complexity(self):
        response = self.test_client.post(
            "http://127.0.0.1:8000/registration_jwt",
            data={
                "login": "newTestUser",
                "password": "superpassword"
            })

        assert response.status_code == 422
        assert response.json()["message"] == ("Слишком простой пароль. Пароль должен содержать"
                                              " заглавные буквы латинского алфавита, а также цифры.")
        assert ("jwt_access_token" in response.cookies) is False

    # Обращение к конечной точке аутентификации с корректными данными
    async def test_authentication_correct_data(self):
        response = self.test_client.post(
            "http://127.0.0.1:8000/authentication_jwt",
            data={
                "login": "newTestUser",
                "password": "newTestUserPassword1"
            })

        assert response.status_code == 200
        assert response.json() == {
            "id": 7,
            "role": "user"
        }
        assert ("jwt_access_token" in response.cookies) is True

    # Обращение к конечной точке аутентификации с неправильным паролем
    async def test_authentication_wrong_password(self):
        response = self.test_client.post(
            "http://127.0.0.1:8000/authentication_jwt",
            data={
                "login": "newTestUser",
                "password": "wrongpassword"
            })

        assert response.status_code == 401
        assert response.json()["message"] == "Неверный пароль."
        assert ("jwt_access_token" in response.cookies) is False

    # Обращение к конечной точке аутентификации с несуществующим логином
    async def test_authentication_nonexistent_user(self):
        response = self.test_client.post(
            "http://127.0.0.1:8000/authentication_jwt",
            data={
                "login": "someuser",
                "password": "somepassword"
            })

        assert response.status_code == 404
        assert response.json()["message"] == "Пользователя с таким логином не существует."
        assert ("jwt_access_token" in response.cookies) is False

    # Обращение к конечной точке получения данных о пользователе с токеном доступа администратора
    async def test_get_user_data_admin_token(self):
        self.test_client.cookies = {"jwt_access_token": create_jwt_token(user_id=5, user_role="admin")}
        response = self.test_client.post("http://127.0.0.1:8000/get_user_data")

        assert response.status_code == 200
        assert response.json() == {
            "id": 5,
            "role": "admin"
        }
        assert ("jwt_access_token" in response.cookies) is True

    # Обращение к конечной точке получения данных о пользователе без токена доступа
    async def test_get_user_data_without_token(self):
        self.test_client.cookies.clear()
        response = self.test_client.post("http://127.0.0.1:8000/get_user_data")

        assert response.status_code == 200
        assert response.json() == {
            "id": 0,
            "role": "guest"
        }
        assert ("jwt_access_token" in response.cookies) is False

    # Запускается в конце каждого теста
    def teardown(self):
        # Возвращаем исходные зависимости
        market_app.dependency_overrides = self.original_dependencies