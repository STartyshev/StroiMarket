import re

from pydantic import BaseModel, field_validator

from api.restrictions.user_data import ErrorField
from api.errors.user_profile.exceptions import InvalidLanguageFormat
from api.schemas.authentication import check_invalid_characters, check_length

invalid_characters = ["!", "@", "#", "$", "%", "^", "&", "*",
                      "(", ")", "-", "+", "=", "{", "}", "[",
                      "]", "|", ";", ":", "'", "\"", "<", ">",
                      "?", "/", "\\", "`", " "]


def check_cyrillic_alphabet(field_to_check: str, error_field: ErrorField):
    cyrillic_format = re.fullmatch(r"[а-яА-Я]+", field_to_check)
    if cyrillic_format is None:
        raise InvalidLanguageFormat(error_field=error_field)


def validate_personal_data(field_to_check: str, error_field: ErrorField):
    check_length(field_to_check=field_to_check, error_field=error_field)
    check_invalid_characters(field_to_check=field_to_check, error_field=error_field)
    check_cyrillic_alphabet(field_to_check=field_to_check, error_field=error_field)
    converted_field = f"{field_to_check[0].upper()}{field_to_check[1:].lower()}"
    return converted_field

class UserPersonalData(BaseModel):
    first_name: str
    last_name: str

    @field_validator("first_name")
    @classmethod
    def validate_first_name(cls, first_name):
        return validate_personal_data(field_to_check=first_name, error_field=ErrorField.first_name)

    @field_validator("last_name")
    @classmethod
    def validate_last_name(cls, last_name):
        return validate_personal_data(field_to_check=last_name, error_field=ErrorField.last_name)
