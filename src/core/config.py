from pydantic_settings import BaseSettings, SettingsConfigDict
import json
import os

from src.schemas.enums import LoggerLevels


class LoggerSettings(BaseSettings):
    LOG_LEVEL: LoggerLevels = LoggerLevels.INFO
    LOG_FILE_PATH: str = "app_data/logs/app.log"
    LOG_ROTATION: str = "10 MB"
    LOG_RETENTION: str = "7 days"
    LOG_COMPRESSION: str = "gz"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


class RedisSettings(BaseSettings):
    REDIS_USER: str | None = None
    REDIS_PASSWORD: str | None = None
    REDIS_DATABASE: int = 0
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    @property
    def redis_url(self):
        if self.REDIS_USER:
            redis_user = self.REDIS_USER
        else:
            redis_user = ""
        if self.REDIS_PASSWORD:
            redis_password = self.REDIS_PASSWORD
        else:
            redis_password = ""
        return f"redis://{redis_user}:{redis_password}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DATABASE}"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


class NsisParserSettings(BaseSettings):
    SITE_URL: str
    PLATE_NUMBER_SELECTOR: str
    VIN_NUMBER_SELECTOR: str
    SEND_FORM_BTN_SELECTOR: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


class GenericSettings(BaseSettings):
    PROXIES_FILE_PATH: str = "proxies.txt"
    HEADLESS: bool = True
    TIMEOUT: float = 10

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


logger_settings = LoggerSettings()
redis_settings = RedisSettings()
nsis_parser = NsisParserSettings()
generic_settings = GenericSettings()
