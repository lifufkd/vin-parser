from fastapi import Request, status
from loguru import logger
from fastapi.responses import JSONResponse

from src.core.exceptions import AppException


async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=exc.headers
    )
