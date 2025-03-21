# tests.user_profile_test.py
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from api.security.authentication import create_jwt_token
from config import settings
from main import market_app
from database.models import User, BonusCard


@pytest_asyncio.fixture(scope="session")
async def test_client():
    with TestClient(market_app) as client:
        yield client


# Тестовый движок, но связан с рабочей БД так как мы тестируем конечные точки без мокинга
@pytest_asyncio.fixture(scope="session")
async def test_async_engine():
    test_engine = create_async_engine(settings.ASYNCPG_DATABASE_URL)
    yield test_engine


# Создаем фабрику сессий
@pytest_asyncio.fixture(scope="session")
async def test_async_session_maker(test_async_engine):
    async_session_maker = async_sessionmaker(test_async_engine, class_=AsyncSession)
    yield async_session_maker


# Создаем сессии
@pytest_asyncio.fixture()
async def async_session(test_async_session_maker):
    async with test_async_session_maker() as async_session:
        yield async_session


# Запрос на конечную точку /user_profile в роли пользователя
@pytest.mark.asyncio
async def test_get_user_profile_data_with_access_token(test_client):
    test_client.cookies.clear()
    test_client.cookies = {"jwt_access_token": create_jwt_token(user_id=39, user_role="user")}

    response = test_client.get("http://127.0.0.1:8000/user_profile/")
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "text/html; charset=utf-8"


# Запрос на конечную точку /user_profile в роли гостя
@pytest.mark.asyncio
async def test_get_user_profile_data_without_access_token(test_client):
    test_client.cookies.clear()

    response = test_client.get("http://127.0.0.1:8000/user_profile/")
    assert response.status_code == 403
    assert (response.json()["message"] ==
            "Недостаточно прав доступа. Чтобы получить доступ к профилю сначала пройдите авторизацию.")


# Запрос на конченую точку /user_profile/update в роли пользователя
# с корректными входными данными
@pytest.mark.asyncio
async def test_update_user_data_with_access_token(test_client):
    test_client.cookies.clear()
    test_client.cookies = {"jwt_access_token": create_jwt_token(user_id=39, user_role="user")}

    response = test_client.patch(
        "http://127.0.0.1:8000/user_profile/update",
        json={
            "first_name": "имя",
            "last_name": "фамилия"
        })

    assert response.status_code == 200
    assert response.json() == {
        "updated_first_name": "Имя",
        "updated_last_name": "Фамилия"
    }


# Запрос на конченую точку /user_profile/update в роли пользователя
# с неправильным языковым форматом данных
@pytest.mark.asyncio
async def test_update_user_data_with_access_token_wrong_language_format(test_client):
    test_client.cookies.clear()
    test_client.cookies = {"jwt_access_token": create_jwt_token(user_id=39, user_role="user")}

    response = test_client.patch(
        "http://127.0.0.1:8000/user_profile/update",
        json={
            "first_name": "first_name",
            "last_name": "last_name"
        })

    assert response.status_code == 422
    assert response.json()["message"] == "Поле \"Имя\" должно содержать только символы кириллицы."


# Запрос на конченую точку /user_profile/update в роли пользователя
# с запрещенным символом в имени
@pytest.mark.asyncio
async def test_update_user_data_with_access_token_invalid_characters_first_name(test_client):
    test_client.cookies.clear()
    test_client.cookies = {"jwt_access_token": create_jwt_token(user_id=39, user_role="user")}

    response = test_client.patch(
        "http://127.0.0.1:8000/user_profile/update",
        json={
            "first_name": "имя!",
            "last_name": "фамилия"
        })

    assert response.status_code == 422
    assert response.json()["message"] == "Имя содержит недопустимые символы."


# Запрос на конченую точку /user_profile/update в роли пользователя
# с запрещенным символом в фамилии
@pytest.mark.asyncio
async def test_update_user_data_with_access_token_invalid_characters_last_name(test_client):
    test_client.cookies.clear()
    test_client.cookies = {"jwt_access_token": create_jwt_token(user_id=39, user_role="user")}

    response = test_client.patch(
        "http://127.0.0.1:8000/user_profile/update",
        json={
            "first_name": "имя",
            "last_name": "фамилия."
        })

    assert response.status_code == 422
    assert response.json()["message"] == "Фамилия содержит недопустимые символы."


# Запрос на конченую точку /user_profile/update в роли пользователя
# с недопустимой длиной имени
@pytest.mark.asyncio
async def test_update_user_data_with_access_token_wrong_length_first_name(test_client):
    test_client.cookies.clear()
    test_client.cookies = {"jwt_access_token": create_jwt_token(user_id=39, user_role="user")}

    response = test_client.patch(
        "http://127.0.0.1:8000/user_profile/update",
        json={
            "first_name": "",
            "last_name": "фамилия"
        })

    assert response.status_code == 422
    assert response.json()["message"] == "Поле \"Имя\" должно иметь длину от 2 до 32 символов включительно."


# Запрос на конченую точку /user_profile/update в роли пользователя
# с недопустимой длиной фамилии
@pytest.mark.asyncio
async def test_update_user_data_with_access_token_wrong_length_last_name(test_client):
    test_client.cookies.clear()
    test_client.cookies = {"jwt_access_token": create_jwt_token(user_id=39, user_role="user")}

    response = test_client.patch(
        "http://127.0.0.1:8000/user_profile/update",
        json={
            "first_name": "имя",
            "last_name": "фамилияфамилияфамилияфамилияфамилия"
        })

    assert response.status_code == 422
    assert response.json()["message"] == "Поле \"Фамилия\" должно иметь длину от 2 до 32 символов включительно."


# Запрос на конченую точку /user_profile/update в роли гостя
@pytest.mark.asyncio
async def test_update_user_data_without(test_client):
    test_client.cookies.clear()

    response = test_client.patch(
        "http://127.0.0.1:8000/user_profile/update",
        json={
            "first_name": "имя",
            "last_name": "фамилия"
        })

    assert response.status_code == 403
    assert response.json()["message"] == ("Недостаточно прав доступа. "
                                          "Чтобы получить доступ к изменению профиля пройдите авторизацию.")



# Запрос на конченую точку /user_profile/delete в роли гостя
@pytest.mark.asyncio
async def test_delete_user_profile_without_access_token(test_client):
    test_client.cookies.clear()

    response = test_client.delete("http://127.0.0.1:8000/user_profile/delete")
    assert response.status_code == 409
    assert response.json()["message"] == "Ошибка доступа. Для удаления профиля необходимо сначала пройти авторизацию."


# Запрос на конченую точку /user_profile/delete в роли пользователя
@pytest.mark.asyncio
async def test_delete_user_profile_with_access_token(test_client, async_session):
    # Чтобы не удалять тестового пользователя из БД создадим нового
    new_test_user = User()
    bonus_card = BonusCard(user=new_test_user)
    async_session.add(new_test_user)
    await async_session.commit()
    await async_session.refresh(new_test_user)

    assert new_test_user.first_name == "Новый"
    assert new_test_user.last_name == "Пользователь"

    test_client.cookies.clear()
    test_client.cookies = {"jwt_access_token": create_jwt_token(user_id=new_test_user.id, user_role=new_test_user.role)}

    response = test_client.delete("http://127.0.0.1:8000/user_profile/delete")
    assert response.status_code == 204


# Запрос на конченую точку /user_profile/exit в роли пользователя
@pytest.mark.asyncio
async def test_user_profile_exit_with_access_token(test_client):
    test_client.cookies.clear()
    test_client.cookies = {"jwt_access_token": create_jwt_token(user_id=39, user_role="user")}

    response = test_client.post("http://127.0.0.1:8000/user_profile/exit")
    assert response.status_code == 204


# Запрос на конченую точку /user_profile/exit в роли гостя
@pytest.mark.asyncio
async def test_user_profile_exit_without_access_token(test_client):
    print(test_client.cookies)
    test_client.cookies.clear()
    print(test_client.cookies)

    response = test_client.post("http://127.0.0.1:8000/user_profile/exit")
    assert response.status_code == 409
    assert response.json()["message"] == ("Ошибка доступа. "
                                          "Не удалось выйти из аккаунта из-за отсутствия авторизации.")
