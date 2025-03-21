from fastapi import APIRouter, Form, Depends
from starlette.responses import JSONResponse

from database.actions import get_user_by_login_from_db, check_login_availability
from database.db import async_session_maker
from database.models import User
from api.schemas.authentication import RegistrationCredentials, AuthCredentials, UserIdRole
from api.security.authentication import create_hashed_password, check_password
from api.errors.authentication.exceptions import UserNotFound, WrongPassword


base_auth = APIRouter()


@base_auth.post('/registration_base')
async def registration(
        credentials: RegistrationCredentials = Form(),
        check_login: bool = Depends(check_login_availability)):
    async with async_session_maker() as async_session:
        hashed_password = create_hashed_password(password=credentials.password)
        new_user = User(login=credentials.login, hashed_password=hashed_password)
        async_session.add(new_user)
        await async_session.commit()
        await async_session.refresh(new_user)
        return UserIdRole.model_validate(new_user)


@base_auth.post('/authentication_base')
async def authentication(credentials: AuthCredentials = Form()):
    async with async_session_maker() as async_session:
        user_from_db = await get_user_by_login_from_db(credentials.login, async_session)
        if user_from_db:
            if check_password(credentials.password, user_from_db.hashed_password):
                return JSONResponse(status_code=200, content=UserIdRole.model_validate(user_from_db).model_dump())
            else:
                raise WrongPassword()
        else:
            raise UserNotFound()
