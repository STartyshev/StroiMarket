# database.actions.py
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import joinedload

import database.db
from api.errors.authentication.exceptions import UnavailableLogin
from api.schemas.authentication import UserIdRole, RegistrationCredentials
from database.db import async_session_maker
from database.models import ImageTable, BonusCard, ProductFeedback
from typing import Type
from database.models import User

async def get_images_from_db(ImagesToFind: Type[ImageTable], DTO: Type[BaseModel], async_session) -> list:
    """
    Функция поиска объектов с информацией об изображениях в БД (в простых таблицах без связей)
    :param ImagesToFind: модель SQLAlchemy описывающая таблицу в БД (class);
    :param DTO: модель DTO (модель для передачи данных в запросе) (class);
    :param async_session: экземпляр асинхронной сессии;
    :return: список объектов, где каждый объект это строка из БД.
    """
    images_from_db = await async_session.execute(select(ImagesToFind))
    images_from_db = images_from_db.scalars().all()
    return [
        DTO.model_validate(image)
        for image in images_from_db
    ]

async def get_user_by_login_from_db(login: str, async_session):
    user_from_db = await async_session.execute(
        select(User)
        .where(User.login == login)
    )
    return user_from_db.scalar()

async def get_user_by_id_from_db(async_session, user: UserIdRole):
    user_from_db = await async_session.execute(
        select(User)
        .where(User.id == user.id)
    )
    return user_from_db.scalar()

async def get_user_with_bonus_card_from_db(async_session, user: UserIdRole):
    user_from_db = await async_session.execute(
        select(User)
        .where(User.id == user.id)
        .options(joinedload(User.bonus_card).joinedload(BonusCard.customer_level))
    )
    return user_from_db.scalar()

async def get_product_feedback_by_id(async_session, feedback_id: int):
    feedback_from_db = await async_session.execute(
        select(ProductFeedback)
        .where(ProductFeedback.id == feedback_id)
    )
    return feedback_from_db.scalar()

async def check_login_availability(credentials: RegistrationCredentials):
    async with async_session_maker() as async_session:
        users_from_db = await get_user_by_login_from_db(credentials.login, async_session)
        if users_from_db:
            raise UnavailableLogin()
        else:
            return True
