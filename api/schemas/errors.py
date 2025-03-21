from pydantic import BaseModel, ValidationError, conint
from fastapi.responses import JSONResponse
from typing import Dict


class ValidatedJSONResponseArgs(BaseModel):
    status_code: conint(ge=200, lt=600)
    error: str
    message: str


class ValidatedJSONResponse(JSONResponse):
    def __init__(self, status_code: int, content: Dict[str, str], *args, **kwargs):
        try:
            ValidatedJSONResponseArgs(status_code=status_code, **content)
            super().__init__(status_code=status_code, content=content, *args, **kwargs)
        except ValidationError:
            super().__init__(
                status_code=500,
                content={
                    "error": "Server error",
                    "message": "Внутренняя ошибка сервера"
                }, *args, **kwargs)
            raise

