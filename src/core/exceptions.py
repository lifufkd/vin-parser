

class AppException(Exception):
    def __init__(self, detail: str | None = None):
        self.detail = detail


class SoftBanError(AppException):
    def __init__(self, detail: str | None = None):
        super().__init__(detail)


class SolidBanError(AppException):
    def __init__(self, detail: str | None = None):
        super().__init__(detail)
