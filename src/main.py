import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.api.v1.router import api_v1_router
from src.core.logger import setup_logger
from src.core.config import cors_settings


@asynccontextmanager
async def lifespan(_: FastAPI):
    setup_logger()
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_settings.CORS_ALLOWED_ORIGINS,
    allow_credentials=cors_settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=cors_settings.CORS_ALLOW_METHODS,
    allow_headers=cors_settings.CORS_ALLOW_HEADERS,
)

app.include_router(api_v1_router, prefix="/api/v1")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
