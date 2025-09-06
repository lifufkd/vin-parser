from fastapi import Request, status
from loguru import logger
from fastapi.responses import JSONResponse

from src.core.exceptions import AppException


async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


async def internal_server_error_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled exception occurred on {request.url}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal Server Error"},
    )
