from fastapi import Request
from fastapi.responses import JSONResponse
from api.errors.authentication.exceptions import (InvalidCharacter,
                                                  InvalidLength,
                                                  InvalidLanguageFormat,
                                                  UnacceptablePasswordComplexity,
                                                  UserNotFound,
                                                  WrongPassword,
                                                  UnavailableLogin)


async def invalid_character_exception_handler(request: Request, exception: InvalidCharacter):
    return JSONResponse(
        status_code=exception.status_code,
        content={"error": exception.detail, "message": exception.message}
    )


async def invalid_length_exception_handler(request: Request, exception: InvalidLength):
    return JSONResponse(
        status_code=exception.status_code,
        content={"error": exception.detail, "message": exception.message}
    )


async def invalid_language_format_exception_handler(request: Request, exception: InvalidLanguageFormat):
    return JSONResponse(
        status_code=exception.status_code,
        content={"error": exception.detail, "message": exception.message}
    )


async def unacceptable_password_complexity_exception_handler(request: Request, exception: UnacceptablePasswordComplexity):
    return JSONResponse(
        status_code=exception.status_code,
        content={"error": exception.detail, "message": exception.message}
    )


async def user_not_found_exception_handler(request: Request, exception: UserNotFound):
    return JSONResponse(
        status_code=exception.status_code,
        content={"error": exception.detail, "message": exception.message}
    )


async def wrong_password_exception_handler(request: Request, exception: WrongPassword):
    return JSONResponse(
        status_code=exception.status_code,
        content={"error": exception.detail, "message": exception.message}
    )


async def unavailable_login_exception_handler(request: Request, exception: UnavailableLogin):
    return JSONResponse(
        status_code=exception.status_code,
        content={"error": exception.detail, "message": exception.message}
    )
