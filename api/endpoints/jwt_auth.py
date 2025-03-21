from fastapi import APIRouter, Form, Depends, Response

from database.actions import check_login_availability, get_user_by_login_from_db
from database.db import async_session_maker
from database.models import User, BonusCard
from api.schemas.authentication import RegistrationCredentials, AuthCredentials, UserIdRole
from api.security.authentication import create_hashed_password, check_password
from api.errors.authentication.exceptions import UserNotFound, WrongPassword
from api.security.authentication import check_jwt_access_token, create_jwt_token


jwt_auth = APIRouter()


@jwt_auth.post('/registration_jwt')
async def registration(
        response: Response,
        credentials: RegistrationCredentials = Form(),
        check_login: bool = Depends(check_login_availability)):
    async with async_session_maker() as async_session:
        hashed_password = create_hashed_password(password=credentials.password)
        new_user = User(login=credentials.login, hashed_password=hashed_password)

        new_bonus_card = BonusCard(user=new_user)

        async_session.add(new_user)
        await async_session.commit()
        await async_session.refresh(new_user)

        jwt_access_token = create_jwt_token(user_id=new_user.id, user_role=new_user.role)

        response.set_cookie(key="jwt_access_token", value=jwt_access_token, max_age=3600, httponly=True)

        return UserIdRole.model_validate(new_user)


@jwt_auth.post('/authentication_jwt')
async def authentication(response: Response, credentials: AuthCredentials = Form()):
    async with async_session_maker() as async_session:
        user_from_db = await get_user_by_login_from_db(credentials.login, async_session)

        if user_from_db:
            if check_password(credentials.password, user_from_db.hashed_password):
                jwt_access_token = create_jwt_token(user_id=user_from_db.id, user_role=user_from_db.role)

                response.set_cookie(key="jwt_access_token", value=jwt_access_token, max_age=3600, httponly=True)

                return UserIdRole.model_validate(user_from_db)
            else:
                raise WrongPassword()
        else:
            raise UserNotFound()


@jwt_auth.post("/get_user_data")
async def get_user_data(user: UserIdRole = Depends(check_jwt_access_token)):
    return user
