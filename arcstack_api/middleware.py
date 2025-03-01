from django.http import HttpRequest, HttpResponse

from .conf import settings
from .errors import APIError, InternalServerError, UnauthorizedError
from .mixins import MiddlewareMixin
from .responses import InternalServerErrorResponse, UnauthorizedResponse
from .serializers import JsonSerializer


class CommonMiddleware(MiddlewareMixin):
    def process_request(self, request):
        meta = getattr(request, '_arcstack_meta', None)

        if meta is None:
            # Not a valid request as an API endpoint
            return

        self._check_login_required(request, meta.endpoint)

        return None

    def process_response(self, request, response):
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
            response = HttpResponse(
                content=f'{response}',
                content_type='text/plain',
            )
        elif JsonSerializer.is_json_serializable(response):
            data = JsonSerializer.serialize(response)
            response = HttpResponse(
                content=data,
                content_type='application/json',
            )
        else:
            raise ValueError(f'Unsupported response type: {type(response)}')

        return response

    def process_exception(
        self, exception: Exception, request: HttpRequest
    ) -> HttpResponse | None:
        response = None

        if isinstance(exception, APIError):
            response = self.process_response(request, exception.message)
            response.status_code = exception.status_code
        elif isinstance(exception, UnauthorizedError):
            response = UnauthorizedResponse()
        elif isinstance(exception, InternalServerError):
            response = InternalServerErrorResponse()

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
