from pydantic_settings import BaseSettings, SettingsConfigDict

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


class CORSSettings(BaseSettings):
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = ["*"]
    CORS_ALLOW_HEADERS: list[str] = ["*"]
    CORS_ALLOWED_ORIGINS: list[str] = []


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
    RESULT_DATA_MODAL_WINDOW_SELECTOR: str
    ERROR_DATA_MODAL_WINDOW_SELECTOR: str
    NOT_FOUND_DATA_MODAL_WINDOW_SELECTOR: str
    BLOCK_PAGE_URL: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


class BrowserSettings(BaseSettings):
    USE_PROXY_BROWSER: bool = False
    USER_AGENT: str
    FETCH_RETRIES_COUNT: int = 3
    FETCH_RETRY_DELAY: int = 2

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


class GenericSettings(BaseSettings):
    PROXIES_FILE_PATH: str = "proxies.txt"
    HEADLESS: bool = True
    TIMEOUT: float = 10
    REQUESTS_DELAY: float = 1
    THREADS: int = 1

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


logger_settings = LoggerSettings()
cors_settings = CORSSettings()
browser_settings = BrowserSettings()
redis_settings = RedisSettings()
nsis_parser = NsisParserSettings()
generic_settings = GenericSettings()
