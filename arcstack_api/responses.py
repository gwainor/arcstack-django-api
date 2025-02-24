import pydantic
from django.http import JsonResponse

from .conf import settings
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


class ErrorResponse(ArcStackResponse):
    def __init__(self, errors: list[pydantic.ValidationError] | str, status: int = 400):
        super().__init__({'error': errors}, status=status)


class InternalServerErrorResponse(ArcStackResponse):
    def __init__(self):
        super().__init__({'error': settings.API_ERROR_RESPONSE_TEXTS[500]}, status=500)


class UnauthorizedResponse(ArcStackResponse):
    def __init__(self):
        super().__init__({'error': settings.API_ERROR_RESPONSE_TEXTS[401]}, status=401)
