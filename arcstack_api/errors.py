import pydantic


# isort: off


class ArcStackError(Exception):
    """Base class for all ArcStack API errors."""

    pass


class ValidationError(ArcStackError):
    def __init__(self, errors: list[pydantic.ValidationError]):
        self.errors = errors
        super().__init__(self.errors)


class APIError(ArcStackError):
    status_code = 400
