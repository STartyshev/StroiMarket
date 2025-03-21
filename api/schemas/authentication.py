import datetime

from pydantic import BaseModel, field_validator, ConfigDict
from api.errors.authentication.exceptions import InvalidCharacter, InvalidLength, InvalidLanguageFormat, UnacceptablePasswordComplexity
from api.restrictions.user_data import ErrorField
import re


invalid_characters = ["!", "@", "#", "$", "%", "^", "&", "*",
                      "(", ")", "-", "+", "=", "{", "}", "[",
                      "]", "|", ";", ":", "'", "\"", "<", ">",
                      "?", "/", "\\", "`", " ", ",", "."]


def check_invalid_characters(field_to_check: str, error_field: ErrorField):
    for invalid_char in invalid_characters:
        if invalid_char in field_to_check:
            raise InvalidCharacter(error_field=error_field)


def check_length(field_to_check: str, error_field: ErrorField):
    field_length = len(field_to_check)
    if (field_length < ErrorField.login.value.min_length or
            field_length > ErrorField.login.value.max_length):
        raise InvalidLength(error_field=error_field)


def check_language_format(field_to_check: str, error_field: ErrorField):
    latin_format = re.fullmatch(r"[a-zA-Z0-9]+", field_to_check)
    if latin_format is None:
        raise InvalidLanguageFormat(error_field=error_field)


def check_password_complexity(field_to_check: str):
    lowercase = any(char.islower() for char in field_to_check)
    uppercase = any(char.isupper() for char in field_to_check)
    digit = any(char.isdigit() for char in field_to_check)

    if not (lowercase and uppercase and digit):
        raise UnacceptablePasswordComplexity()


class BaseCredentials:
    login: str
    password: str


class RegistrationCredentials(BaseModel, BaseCredentials):
    # Проверка значений при их изменении + позволяет использовать model_validate без from_attributes=True
    model_config = ConfigDict(from_attributes=True, validate_assignment=True)

    @field_validator("login")
    @classmethod
    def validate_login(cls, login):
        check_invalid_characters(login, ErrorField.login)
        check_length(login, ErrorField.login)
        check_language_format(login, ErrorField.login)
        return login

    @field_validator("password")
    @classmethod
    def validate_password(cls, password):
        check_invalid_characters(password, ErrorField.password)
        check_length(password, ErrorField.password)
        check_language_format(password, ErrorField.password)
        check_password_complexity(password)
        return password


class AuthCredentials(BaseModel, BaseCredentials):
    model_config = ConfigDict(from_attributes=True, validate_assignment=True)


class UserIdRole(BaseModel):
    model_config = ConfigDict(from_attributes=True, validate_assignment=True)

    id: int
    role: str


class UserFull(BaseModel):
    model_config = ConfigDict(from_attributes=True, validate_assignment=True)

    id: int
    first_name: str
    last_name: str
    phone_number: str | None
    email: str | None
    login: str
    role: str
    total_amount_of_purchases: float
    date_of_registration: datetime.datetime
    date_of_update: datetime.datetime
