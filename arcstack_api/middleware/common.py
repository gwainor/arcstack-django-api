from django.http import HttpRequest, HttpResponse

from ..errors import APIError
from ..responses import JsonResponse
from ..serializers import JsonSerializer
from .mixin import MiddlewareMixin


class CommonMiddleware(MiddlewareMixin):
    def process_response(self, request, response, *args, **kwargs):
        if isinstance(response, HttpResponse):
            # noop: The response is already an HttpResponse
            pass
        elif (
            isinstance(response, str)
            or isinstance(response, int)
            or isinstance(response, float)
            or isinstance(response, bool)
        ):
            # Convert the response to a string and return it as an HttpResponse
            response = HttpResponse(content=f'{response}')
        elif JsonSerializer.is_json_serializable(response):
            data = JsonSerializer.serialize(response)
            response = HttpResponse(content=data, content_type='application/json')
        else:
            raise ValueError(f'Unsupported response type: {type(response)}')

        return response

    def process_exception(
        self, exception: Exception, request: HttpRequest
    ) -> HttpResponse | None:
        response = None

        if isinstance(exception, APIError):
            response = JsonResponse(
                {
                    'error': exception.message,
                    'status': exception.status_code,
                },
                status=exception.status_code,
            )

        return response
