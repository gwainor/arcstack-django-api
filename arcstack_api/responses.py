import pydantic
from django.http import JsonResponse

from .encoders import ArcStackJSONEncoder


# isort: off


class ArcStackResponse(JsonResponse):
    def __init__(
        self,
        data,
        encoder=ArcStackJSONEncoder,
        safe=True,
        json_dumps_params=None,
        **kwargs,
    ):
        super().__init__(
            data,
            encoder=encoder,
            safe=safe,
            json_dumps_params=json_dumps_params,
            **kwargs,
        )


class HttpMethodNotAllowedResponse(ArcStackResponse):
    status_code = 405

    def __init__(self):
        super().__init__({'error': 'Method not allowed'})


class ValidationErrorResponse(ArcStackResponse):
    status_code = 400

    def __init__(self, errors: list[pydantic.ValidationError] | str):
        super().__init__({'error': errors})


class UnauthorizedResponse(ArcStackResponse):
    status_code = 401

    def __init__(self):
        super().__init__({'error': 'Unauthorized'})
