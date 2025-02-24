import pydantic

from .conf import settings


# isort: off


class ArcStackError(Exception):
    """Base class for all ArcStack API errors."""

    pass


class HttpError(ArcStackError):
    """HttpError means an error raised and should be sent as a HTTP response"""

    status_code: int = 400


class ValidationError(HttpError):
    status_code = 400

    def __init__(self, errors: list[pydantic.ValidationError]):
        self.errors = errors
        super().__init__(self.errors)


class APIError(HttpError):
    status_code = 400


class HttpMethodNotAllowedError(HttpError):
    status_code = 405

    def __init__(self):
        super().__init__(settings.API_ERROR_RESPONSE_TEXTS[405])
