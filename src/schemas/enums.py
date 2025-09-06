from enum import Enum


class LoggerLevels(Enum):
    TRACE = "TRACE"
    DEBUG = "DEBUG"
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class SearchStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    NOT_FOUND = "NOT_FOUND"
