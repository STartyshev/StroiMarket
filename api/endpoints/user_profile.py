from fastapi import APIRouter, Depends, Request, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from starlette.responses import JSONResponse

from api.schemas.authentication import UserIdRole
from api.schemas.user_profile import UserPersonalData
from api.security.authentication import check_jwt_access_token, set_empty_jwt_access_token
from database.actions import get_user_with_bonus_card_from_db, get_user_by_id_from_db
from database.db import async_session_maker
from database.models import CustomerLevel

user_profile_router = APIRouter(prefix="/user_profile")
templates = Jinja2Templates(directory="templates")

@user_profile_router.get("/")
async def get_user_profile_data(request: Request, user: UserIdRole = Depends(check_jwt_access_token)):
    if user.role == "user":
        async with async_session_maker() as async_session:
            user_from_db = await get_user_with_bonus_card_from_db(async_session, user)

            # Поиск уровня бонусной карты, который на один выше чем уровень у пользователя
            customer_level_from_db = await async_session.execute(
                select(CustomerLevel)
                .where(CustomerLevel.level_number == user_from_db.bonus_card.customer_level.level_number + 1)
            )
            customer_level_from_db = customer_level_from_db.scalar()

            if customer_level_from_db:
                # Пользователь не достиг последнего уровня бонусной карты
                bonus_card_max_level_message = False
                amount_of_purchases_to_next_level = customer_level_from_db.lower_threshold - user_from_db.total_amount_of_purchases
            else:
                # Пользователь достиг последнего уровня поэтому сообщаем ему об этом
                bonus_card_max_level_message = True

            return templates.TemplateResponse(
                request,
                name="user_profile.html",
                context={
                    "first_name": user_from_db.first_name,
                    "last_name": user_from_db.last_name,
                    "phone_number": user_from_db.phone_number if user_from_db.phone_number is not None else "",
                    "email": user_from_db.email if user_from_db.email is not None else "",
                    "bonus_card": user_from_db.bonus_card,
                    "amount_of_purchases_to_next_level": amount_of_purchases_to_next_level,
                    "bonus_card_max_level_message": bonus_card_max_level_message
                }
            )
    else:
        return JSONResponse(
            status_code=403,
            content={
                "message": "Недостаточно прав доступа. Чтобы получить доступ к профилю сначала пройдите авторизацию."
            })


@user_profile_router.patch("/update")
async def update_user_data(fields_to_update: UserPersonalData, user: UserIdRole = Depends(check_jwt_access_token)):
    print(user.id)
    if user.role == "user":
        async with async_session_maker() as async_session:
            user_from_db = await get_user_by_id_from_db(async_session, user)

            # Обновляем персональные данные (новые данные уже прошли валидацию)
            user_from_db.first_name = fields_to_update.first_name
            user_from_db.last_name = fields_to_update.last_name

            await async_session.commit()
            await async_session.refresh(user_from_db)

            return {
                "updated_first_name": user_from_db.first_name,
                "updated_last_name": user_from_db.last_name
            }
    else:
        return JSONResponse(
            status_code=403,
            content={
                "message": "Недостаточно прав доступа. "
                           "Чтобы получить доступ к изменению профиля пройдите авторизацию."
            })


@user_profile_router.delete("/delete")
async def delete_user_profile(response: Response, user: UserIdRole = Depends(check_jwt_access_token)):
    if user.role == "user":
        async with async_session_maker() as async_session:
            user_from_db = await get_user_by_id_from_db(async_session, user)

            await async_session.delete(user_from_db)
            await async_session.commit()

            return set_empty_jwt_access_token(response)
    else:
        return JSONResponse(status_code=409, content={
            "message": "Ошибка доступа. Для удаления профиля необходимо сначала пройти авторизацию."
        })


@user_profile_router.post("/exit")
async def user_profile_exit(response: Response, user = Depends(check_jwt_access_token)):
    if user.role == "user":
        return set_empty_jwt_access_token(response)
    else:
        return JSONResponse(status_code=409, content={
            "message": "Ошибка доступа. Не удалось выйти из аккаунта из-за отсутствия авторизации."
        })
