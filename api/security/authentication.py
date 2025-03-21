import bcrypt
from jose import jwt
from fastapi import Request, Response
from datetime import datetime, timedelta, timezone

from config import settings
from api.schemas.authentication import UserIdRole


def create_hashed_password(password: str):
    return bcrypt.hashpw(password=password.encode('utf-8'), salt=bcrypt.gensalt())


def check_password(password: str, hashed_password: bytes):
    return bcrypt.checkpw(password=password.encode('utf-8'), hashed_password=hashed_password)


def create_jwt_token(user_id: int, user_role: str = "guest"):
    payload = {
        "id": user_id,
        "role": user_role,
        "exp": datetime.now(timezone.utc) + timedelta(hours=1)
    }
    return jwt.encode(claims=payload, key=settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_jwt_empty_token():
    payload = {}
    return jwt.encode(claims=payload, key=settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def check_jwt_access_token(request: Request, response: Response):
    jwt_access_token = request.cookies.get("jwt_access_token")

    if jwt_access_token:
        payload = jwt.decode(jwt_access_token, key=settings.SECRET_KEY, algorithms=settings.JWT_ALGORITHM)
        new_jwt_access_token = create_jwt_token(user_id=payload["id"], user_role=payload["role"])
        response.set_cookie(key="jwt_access_token", value=new_jwt_access_token, max_age=3600, httponly=True)
        return UserIdRole.model_validate(payload)
    else:
        return UserIdRole(id=0, role="guest")


def set_empty_jwt_access_token(response: Response):
    empty_jwt_access_token = create_jwt_empty_token()
    response.set_cookie(key="jwt_access_token", value=empty_jwt_access_token, max_age=0, httponly=True)
    response.status_code = 204
    return response
