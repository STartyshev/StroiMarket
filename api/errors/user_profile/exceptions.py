from fastapi import HTTPException
from api.restrictions.user_data import ErrorField


class InvalidLanguageFormat(HTTPException):
    def __init__(self, error_field: ErrorField, status_code: int = 422):
        detail = f"Invalid language format in {error_field.value.name_eng}"
        message = f"Поле \"{error_field.value.name_ru}\" должно содержать только символы кириллицы."
        super().__init__(status_code=status_code, detail=detail)
        self.message = message


class InvalidLength(HTTPException):
    def __init__(self, error_field: ErrorField, status_code: int = 422):
        detail = f"Invalid {error_field.value.name_eng} length"
        message = (f"Поле \"{error_field.value.name_ru}\" должно иметь длину от {error_field.value.min_length} "
                   f"до {error_field.value.max_length} символов включительно.")
        super().__init__(status_code=status_code, detail=detail)
        self.message = message


class InvalidCharacter(HTTPException):
    def __init__(self, error_field: ErrorField, status_code: int = 422):
        detail = f"Invalid character in {error_field.value.name_eng}"
        message = f"{error_field.value.name_ru} содержит недопустимые символы."
        super().__init__(status_code=status_code, detail=detail)
        self.message = message