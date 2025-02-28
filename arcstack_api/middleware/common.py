from django.http import HttpRequest, HttpResponse

from ..conf import settings
from ..errors import APIError, UnauthorizedError
from ..responses import JsonResponse, UnauthorizedResponse
from ..serializers import JsonSerializer
from .mixin import MiddlewareMixin


class CommonMiddleware(MiddlewareMixin):
    def process_request(self, request, *args, **kwargs):
        endpoint = getattr(request, 'endpoint', None)

        if endpoint is None:
            # Not a valid request as an API endpoint
            return

        self._check_login_required(request, endpoint)

        return None

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
        elif isinstance(exception, UnauthorizedError):
            response = UnauthorizedResponse()

        # Not an exception defined in the ArcStack API.
        # Let the other middleware handle it.

        return response

    def _check_login_required(self, request, endpoint):
        """Check if the request is authenticated.

        If the endpoint is a class-based view, the `login_required` attribute
        will be checked. Otherwise, the `login_required` function attribute
        will be checked.
        """
        login_required = settings.API_DEFAULT_LOGIN_REQUIRED

        func = endpoint.view_class if hasattr(endpoint, 'view_class') else endpoint

        if hasattr(func, 'LOGIN_REQUIRED') and isinstance(func.LOGIN_REQUIRED, bool):
            login_required = func.LOGIN_REQUIRED

        if login_required and not request.user.is_authenticated:
            raise UnauthorizedError()

        return None
