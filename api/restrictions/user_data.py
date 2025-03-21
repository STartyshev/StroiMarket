from enum import Enum


class UserInfoField:
    def __init__(self, name_eng: str, name_ru: str, min_length: int, max_length: int = 32):
        self.name_eng = name_eng
        self.name_ru = name_ru
        self.min_length = min_length
        self.max_length = max_length


class ErrorField(Enum):
    login = UserInfoField(name_eng="login", name_ru="Логин", min_length=3)
    password = UserInfoField(name_eng="password", name_ru="Пароль", min_length=12)
    first_name = UserInfoField(name_eng="first name", name_ru="Имя", min_length=2)
    last_name = UserInfoField(name_eng="last name", name_ru="Фамилия", min_length=2)
