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


class MethodNotAllowedResponse(HttpResponse):
    def __init__(self):
        super().__init__(
            content=b'Method not allowed',
            status=405,
        )


class NotFoundResponse(HttpResponse):
    def __init__(self):
        super().__init__(
            content=b'Not found',
            status=404,
        )


class UnauthorizedResponse(HttpResponse):
    def __init__(self):
        super().__init__(
            content=b'Unauthorized',
            status=401,
        )
