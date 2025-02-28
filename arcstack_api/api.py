from collections.abc import Callable
from functools import wraps
from typing import Annotated

from django.core.exceptions import ImproperlyConfigured, MiddlewareNotUsed
from django.http import HttpRequest, HttpResponse
from django.utils.module_loading import import_string
from typing_extensions import Doc

from .conf import settings
from .errors import ValidationError
from .logger import logger
from .responses import InternalServerErrorResponse
from .serializers import JsonSerializer
from .signature import EndpointSignature


class ArcStackAPI:
    _param_middleware: Annotated[
        list[Callable],
        Doc(
            """
            Middleware that will be called to build the endpoint kwargs.
            Should accept the following arguments:
            - request: The request object.
            - signature: The signature of the endpoint.
            - callback_args: The arguments of the callback.
            - callback_kwargs: The keyword arguments of the callback.
            Should return a tuple of (kwargs, response).
            - kwargs: The keyword arguments to pass to the endpoint. Must be a
              dictionary. `None` can be returned if there is nothing to add.
            - response: The response to return. If the response is not None,
              the execution will be terminated because there is probably a
              validation error.
            """
        ),
    ] = []

    _exception_middleware: Annotated[
        list[Callable],
        Doc(
            """
            Middleware that will be called to process the exception.
            Should accept the following arguments:
            - exception: The exception to process.
            - request: The request object.
            Should return a response.
            """
        ),
    ] = []

    _middleware_chain: Annotated[
        Callable,
        Doc(
            """
            The middleware chain.
            """
        ),
    ] = None

    def __init__(self):
        self.load_middleware()

    def load_middleware(self):
        self._param_middleware = []
        self._exception_middleware = []
        handler = self._get_response
        for middleware_path in reversed(settings.API_MIDDLEWARE):
            middleware = import_string(middleware_path)

            try:
                mw_instance = middleware(handler)
            except MiddlewareNotUsed as e:
                if settings.DEBUG:
                    if str(e):
                        logger.debug(f'MiddlewareNotUsed({middleware_path}): {e}')
                    else:
                        logger.debug(f'MiddlewareNotUsed({middleware_path})')
                continue
            else:
                handler = mw_instance

            if mw_instance is None:
                raise ImproperlyConfigured(
                    f'Middleware factory {middleware_path} returned None.'
                )

            if hasattr(mw_instance, 'process_params'):
                self._param_middleware.insert(0, mw_instance.process_params)
            if hasattr(mw_instance, 'process_exception'):
                self._exception_middleware.append(mw_instance.process_exception)

        self._middleware_chain = handler

    def __call__(self, endpoint: Callable):
        wrapper = self._create_wrapper(endpoint)
        return wrapper

    def _create_wrapper(self, endpoint: Callable):
        @wraps(endpoint)
        def wrapper(request, *args, **kwargs):
            request.endpoint = endpoint
            request.signature = EndpointSignature(endpoint)

            try:
                response = self._middleware_chain(request, *args, **kwargs)
            except Exception as e:
                response = self._process_exception(e, request)

            return response

        return wrapper

    def _get_response(self, request, *args, **kwargs):
        if not hasattr(request, 'endpoint'):
            raise ImproperlyConfigured(
                'The request object must have an `endpoint` attribute. '
                'To endpointize a view, use the `api` decorator or '
                'subclass `Endpoint`.'
            )

        response, endpoint_args, endpoint_kwargs = self._process_params(
            request, *args, **kwargs
        )

        if response is None:
            response = request.endpoint(request, *endpoint_args, **endpoint_kwargs)

        return response

    def _process_params(self, request, *args, **kwargs):
        """Process the parameters of the request through the middleware."""
        response = None

        validation_errors = []
        for middleware in self._param_middleware:
            try:
                args, kwargs = middleware(args, kwargs)
            except ValidationError as e:
                validation_errors.append(e)
            except Exception as e:
                response = self._process_exception(e, request)

        if validation_errors:
            response = HttpResponse(
                content=JsonSerializer.serialize(
                    {
                        'errors': [str(e) for e in validation_errors],
                    }
                ),
                status=400,
            )

        return response, args, kwargs

    def _process_exception(
        self, exception: Exception, request: HttpRequest
    ) -> HttpResponse | None:
        """Process the exception through the middleware."""
        response = None

        for middleware in self._exception_middleware:
            try:
                response = middleware(exception, request)
                if response is not None:
                    break
            except Exception as e:
                # Another exception occurred in the exception middleware.
                # Let it propagate.
                response = self._process_unhandled_exception(e)

        # No response means no middleware handled the exception. There is a built-in
        # (`CommonMiddleware`) middleware that handles the API errors but it seems
        # it is ommitted from the middleware chain.
        # Let's hope the developer knows what they are doing.
        if response is None:
            response = self._process_unhandled_exception(exception)

        return response

    def _process_unhandled_exception(self, exception: Exception):
        """Process the unhandled exception."""
        if settings.DEBUG:
            raise exception
        else:
            logger.error(f'Unhandled exception: {exception}')
            return InternalServerErrorResponse()


arcstack_api = ArcStackAPI()
