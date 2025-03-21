from api.errors.headers.exceptions import HeaderMissing
from fastapi import Request
from fastapi.responses import JSONResponse


async def header_missing_exception_handler(request: Request, exception: HeaderMissing):
    return JSONResponse(
        status_code=exception.status_code,
        content={
            "error": exception.detail,
            "message": exception.message
        }
    )
