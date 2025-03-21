# api.errors.register_handlers.py
from fastapi import FastAPI
from fastapi import Request

from api.errors.authentication import exceptions as auth_exc, handlers as auth_handlers
from api.errors.user_profile import exceptions as user_profile_exc, handlers as user_profile_handlers


def register_exception_handlers(app: FastAPI):
    @app.exception_handler(auth_exc.InvalidCharacter)
    async def invalid_character_exception_handler_(request: Request, exception: auth_exc.InvalidCharacter):
        return await auth_handlers.invalid_character_exception_handler(request=request, exception=exception)

    @app.exception_handler(auth_exc.InvalidLength)
    async def invalid_length_exception_handler_(request: Request, exception: auth_exc.InvalidLength):
        return await auth_handlers.invalid_length_exception_handler(request=request, exception=exception)

    @app.exception_handler(auth_exc.InvalidLanguageFormat)
    async def invalid_language_format_exception_handler_(request: Request, exception: auth_exc.InvalidLanguageFormat):
        return await auth_handlers.invalid_language_format_exception_handler(request=request, exception=exception)

    @app.exception_handler(auth_exc.UnacceptablePasswordComplexity)
    async def unacceptable_password_complexity_exception_handler_(request: Request,
                                                                  exception: auth_exc.UnacceptablePasswordComplexity):
        return await auth_handlers.unacceptable_password_complexity_exception_handler(request=request, exception=exception)

    @app.exception_handler(auth_exc.UserNotFound)
    async def user_not_found_format_exception_handler_(request: Request, exception: auth_exc.UserNotFound):
        return await auth_handlers.user_not_found_exception_handler(request=request, exception=exception)

    @app.exception_handler(auth_exc.WrongPassword)
    async def wrong_password_exception_handler_(request: Request, exception: auth_exc.WrongPassword):
        return await auth_handlers.wrong_password_exception_handler(request=request, exception=exception)

    @app.exception_handler(auth_exc.UnavailableLogin)
    async def unavailable_login_exception_handler_(request: Request, exception: auth_exc.UnavailableLogin):
        return await auth_handlers.unavailable_login_exception_handler(request=request, exception=exception)

    @app.exception_handler(user_profile_exc.InvalidCharacter)
    async def invalid_character_exception_handler_(request: Request, exception: user_profile_exc.InvalidCharacter):
        return await user_profile_handlers.invalid_character_exception_handler(request=request, exception=exception)

    @app.exception_handler(user_profile_exc.InvalidLanguageFormat)
    async def invalid_language_format_exception_handler_(request: Request, exception: user_profile_exc.InvalidLanguageFormat):
        return await user_profile_handlers.invalid_language_format_exception_handler(request=request, exception=exception)

    @app.exception_handler(user_profile_exc.InvalidLength)
    async def invalid_length_exception_handler_(request: Request, exception: user_profile_exc.InvalidLength):
        return await user_profile_handlers.invalid_length_exception_handler(request=request, exception=exception)
