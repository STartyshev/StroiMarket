from fastapi import HTTPException


class HeaderMissing(HTTPException):
    def __init__(self, header_name: str, status_code: int = 400):
        detail = f"Header \"{header_name}\" is missing"
        message = f"Заголовок \"{header_name}\" отсутствует"
        super().__init__(status_code=status_code, detail=detail)
        self.message = message
