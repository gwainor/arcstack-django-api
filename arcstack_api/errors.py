# pragma: exclude file

from typing import Any


class APIError(Exception):
    """Represents errors that should be returned as a response.

    Classes that inherit from this class should modify the `status_code`
    and `message` attributes.
    """

    def __init__(self, message: Any, status_code: int = 400):
        self.message = message
        self.status_code = status_code

    def __str__(self):
        return f'{self.status_code} {self.message}'


class InternalServerError(Exception):
    """Represents errors that should be returned as a 500 response."""

    def __init__(self):
        super().__init__('Internal server error')
        self.status_code = 500


class ValidationError(Exception):
    """Validation errors occurs when processing the input data such as query
    parameters, path parameters, headers, cookies, request body, etc.
    """

    def __init__(self, message: str):
        super().__init__(message)


class UnauthorizedError(Exception):
    """Represents errors that should be returned as a 401 response."""

    def __init__(self):
        super().__init__('Unauthorized')
        self.status_code = 401
