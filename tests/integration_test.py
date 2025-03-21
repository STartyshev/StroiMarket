#tests.integration_test.py
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from unittest.mock import MagicMock
from sqlalchemy import select

from config import settings
from main import market_app
from database.db import Base, async_session_maker as asm
from database.models import CustomerLevel


@pytest.mark.asyncio
class TestScenarios:
    @pytest_asyncio.fixture(scope="session")
    async def test_client(self):
        async with AsyncClient(transport=ASGITransport(app=market_app)) as client:
            yield client

    # Вызывается перед каждым тестом
    @pytest.fixture(autouse=True)
    def setup(self, test_client):
        self.test_client = test_client

    @pytest_asyncio.fixture
    async def async_engine(self):
        async_engine_ = create_async_engine(settings.ASYNCPG_TEST_DATABASE_URL)

        async with async_engine_.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

            # Берем данные по уровням бонусных карт из реальной БД,
            # так как бонусная карта зависит от таблицы уровней и
            # автоматически создается вместе с пользователем,
            # а наша текущая БД пустая
            async with asm() as async_session_:
                bonus_card_from_real_db = await async_session_.execute(select(CustomerLevel))
                bonus_card_from_real_db = bonus_card_from_real_db.scalars().all()

            for card in bonus_card_from_real_db:
                await conn.execute(CustomerLevel.__table__.insert().values({
                    "name": card.name,
                    "discount_amount_in_percent": card.discount_amount_in_percent,
                    "lower_threshold": card.lower_threshold,
                    "level_number": card.level_number
                }))

        yield async_engine_

        async with async_engine_.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

        await async_engine_.dispose()

    @pytest_asyncio.fixture
    async def async_session_maker(self, async_engine):
        async_session_maker_ = async_sessionmaker(bind=async_engine, class_=AsyncSession)
        yield async_session_maker_

    @pytest_asyncio.fixture
    async def async_session(self, async_session_maker):
        async with async_session_maker() as async_session_:
            yield async_session_

    @pytest.fixture(autouse=True)
    def mock_async_session_maker_(self, mocker, async_session):
        mock_async_session_maker = MagicMock()
        mock_async_session_maker.return_value.__aenter__.return_value = async_session
        mock_async_session_maker.return_value.__aexit__.return_value = None

        mocker.patch("database.actions.async_session_maker", new=mock_async_session_maker)
        mocker.patch("api.endpoints.jwt_auth.async_session_maker", new=mock_async_session_maker)
        mocker.patch("api.endpoints.user_profile.async_session_maker", new=mock_async_session_maker)

        return mock_async_session_maker

    @pytest.mark.asyncio
    async def test_first_scenario(self):
        # Проходим регистрацию
        response = await self.test_client.post(
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

        # После регистрации меняем свои личные данные
        response = await self.test_client.patch(
            "http://127.0.0.1:8000/user_profile/update",
            json={
                "first_name": "НОВОЕимя",
                "last_name": "новаяФАМИЛИЯ"
            })

        assert response.status_code == 200
        assert response.json() == {
            "updated_first_name": "Новоеимя",
            "updated_last_name": "Новаяфамилия"
        }

        # Выходим из профиля
        response = await self.test_client.post("http://127.0.0.1:8000/user_profile/exit")
        assert response.status_code == 204

        # Пытаемся пройти регистрацию с теми же данными, что и в начале
        response = await self.test_client.post(
            "http://127.0.0.1:8000/registration_jwt",
            data={
                "login": "newTestUser",
                "password": "newTestUser1"
            })

        assert response.status_code == 409
        assert response.json()["message"] == "Пользователь с таким логином уже существует."
        assert ("jwt_access_token" in response.cookies) is False

        # Пытаемся зайти на страницу с профилем
        # Несмотря на то, что при выходе из профиля мы устанавливаем пустой токен доступа
        # со сроком действия 0 в AsyncClient он не исчезает, поэтому удаляем вручную
        self.test_client.cookies.clear()
        response = await self.test_client.get("http://127.0.0.1:8000/user_profile/")
        assert response.status_code == 403
        assert (response.json()["message"] ==
                "Недостаточно прав доступа. Чтобы получить доступ к профилю сначала пройдите авторизацию.")

        # Пытаемся залогиниться с опечаткой в пароле
        response = await self.test_client.post(
            "http://127.0.0.1:8000/authentication_jwt",
            data={
                "login": "newTestUser",
                "password": "newTestuser1"
            })

        assert response.status_code == 401
        assert response.json()["message"] == "Неверный пароль."
        assert ("jwt_access_token" in response.cookies) is False

        # Теперь с правильными данными
        response = await self.test_client.post(
            "http://127.0.0.1:8000/authentication_jwt",
            data={
                "login": "newTestUser",
                "password": "newTestUser1"
            })

        assert response.status_code == 200
        assert response.json() == {
            "id": 1,
            "role": "user"
        }
        assert ("jwt_access_token" in response.cookies) is True

        # Заходим на страницу профиля
        response = await self.test_client.get("http://127.0.0.1:8000/user_profile/")
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "text/html; charset=utf-8"

        # Удаляем профиль
        response = await self.test_client.delete("http://127.0.0.1:8000/user_profile/delete")
        assert response.status_code == 204
