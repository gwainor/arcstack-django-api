from django.http import HttpResponse
from django.http import JsonResponse as DjangoJsonResponse

from .serializers import JsonSerializer


class JsonResponse(DjangoJsonResponse):
    def __init__(self, data, status=200):
        super().__init__(
            data,
            status=status,
            encoder=JsonSerializer._get_default_encoder(),
        )


class InternalServerErrorResponse(HttpResponse):
    def __init__(self):
        super().__init__(content=b'Internal server error', status=500)
