from fastapi import APIRouter, Form, Depends, Response

from database.actions import get_user_by_login_from_db, check_login_availability
from database.db import async_session_maker
from database.models import User
from api.schemas.authentication import RegistrationCredentials, AuthCredentials, UserIdRole
from api.security.authentication import create_hashed_password, check_password
from api.errors.authentication.exceptions import UserNotFound, WrongPassword
from itsdangerous import URLSafeTimedSerializer
from config import settings


cookie_auth = APIRouter()
serializer = URLSafeTimedSerializer(settings.SECRET_KEY)


@cookie_auth.post('/registration_cookie')
async def registration(
        response: Response,
        credentials: RegistrationCredentials = Form(),
        check_login: bool = Depends(check_login_availability)):
    async with async_session_maker() as async_session:
        hashed_password = create_hashed_password(password=credentials.password)

        new_user = User(login=credentials.login, hashed_password=hashed_password)
        async_session.add(new_user)
        await async_session.commit()
        await async_session.refresh(new_user)

        access_token = serializer.dumps({"id": new_user.id, "role": new_user.role})
        response.set_cookie(key="access_token", value=access_token, max_age=3600, httponly=True)

        return UserIdRole.model_validate(new_user)


@cookie_auth.post('/authentication_cookie')
async def authentication(response: Response, credentials: AuthCredentials = Form()):
    async with async_session_maker() as async_session:
        user_from_db = await get_user_by_login_from_db(credentials.login, async_session)

        if user_from_db:
            if check_password(credentials.password, user_from_db.hashed_password):
                access_token = serializer.dumps({"id": user_from_db.id, "role": user_from_db.role})
                response.set_cookie(key="access_token", value=access_token, max_age=3600, httponly=True)

                return UserIdRole.model_validate(user_from_db)
            else:
                raise WrongPassword()
        else:
            raise UserNotFound()
