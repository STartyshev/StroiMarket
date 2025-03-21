from fastapi import HTTPException
from api.restrictions.user_data import ErrorField


class InvalidCharacter(HTTPException):
    def __init__(self, error_field: ErrorField, status_code: int = 422):
        detail = f"Invalid character in {error_field.value.name_eng}"
        message = f"{error_field.value.name_ru} содержит недопустимые символы."
        super().__init__(status_code=status_code, detail=detail)
        self.message = message


class InvalidLength(HTTPException):
    def __init__(self, error_field: ErrorField, status_code: int = 422):
        detail = f"Invalid {error_field.value.name_eng} length"
        message = (f"Поле \"{error_field.value.name_ru}\" должно иметь длину "
                   f"от {error_field.value.min_length} до {error_field.value.max_length} символов включительно.")
        super().__init__(status_code=status_code, detail=detail)
        self.message = message


class InvalidLanguageFormat(HTTPException):
    def __init__(self, error_field: ErrorField, status_code: int = 422):
        detail = f"Invalid language format in {error_field.value.name_eng}"
        message = f"{error_field.value.name_ru} должен содержать символы только латинского алфавита."
        super().__init__(status_code=status_code, detail=detail)
        self.message = message


class UnacceptablePasswordComplexity(HTTPException):
    def __init__(
            self,
            status_code: int = 422,
            detail: str = "Unacceptable password complexity",
            message: str = "Слишком простой пароль. "
                           "Пароль должен содержать заглавные буквы латинского алфавита, а также цифры."
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.message = message


class UserNotFound(HTTPException):
    def __init__(self,
                 status_code: int = 404,
                 detail: str = "User not found",
                 message: str = "Пользователя с таким логином не существует."):
        super().__init__(status_code=status_code, detail=detail)
        self.message = message


class WrongPassword(HTTPException):
    def __init__(self,
                 status_code: int = 401,
                 detail: str = "User unauthorized. Wrong password",
                 message: str = "Неверный пароль."):
        super().__init__(status_code=status_code, detail=detail)
        self.message = message


class UnavailableLogin(HTTPException):
    def __init__(self,
                 status_code: int = 409,
                 detail: str = "Login already exists",
                 message: str = "Пользователь с таким логином уже существует."):
        super().__init__(status_code=status_code, detail=detail)
        self.message = message
