from fastapi import status


class AppException(Exception):
    def __init__(self, detail: str | None = None, status_code: int = status.HTTP_400_BAD_REQUEST, headers: dict | None = None):
        self.detail = detail
        self.status_code = status_code
        self.headers = headers


class SoftBanError(AppException):
    def __init__(self, detail: str | None = None):
        super().__init__(detail=detail)


class SolidBanError(AppException):
    def __init__(self, detail: str | None = None):
        super().__init__(detail=detail)


class AllProxiesBanedError(AppException):
    def __init__(self, detail: str = "All proxies baned, can't continue"):
        super().__init__(detail=detail)
