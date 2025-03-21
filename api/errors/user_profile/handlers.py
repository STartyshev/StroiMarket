from fastapi import Request
from fastapi.responses import JSONResponse

from api.errors.user_profile.exceptions import InvalidCharacter, InvalidLanguageFormat, InvalidLength

async def invalid_character_exception_handler(request: Request, exception: InvalidCharacter):
    return JSONResponse(
        status_code=exception.status_code,
        content={
            "error": exception.detail,
            "message": exception.message
        }
    )


async def invalid_language_format_exception_handler(request: Request, exception: InvalidLanguageFormat):
    return JSONResponse(
        status_code=exception.status_code,
        content={
            "error": exception.detail,
            "message": exception.message
        }
    )


async def invalid_length_exception_handler(request: Request, exception: InvalidLength):
    return JSONResponse(
        status_code=exception.status_code,
        content={
            "error": exception.detail,
            "message": exception.message
        }
    )
