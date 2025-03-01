from collections.abc import Callable
from functools import wraps
from typing import Annotated

from django.core.exceptions import ImproperlyConfigured, MiddlewareNotUsed
from django.http import HttpRequest, HttpResponse
from django.utils.module_loading import import_string
from typing_extensions import Doc

from .conf import settings
from .logger import logger
from .meta import ArcStackRequestMeta
from .responses import InternalServerErrorResponse


class ArcStackAPI:
    _endpoint_middleware: Annotated[
        list[Callable],
        Doc(
            """
            Middleware that will be called to build the endpoint kwargs.
            Should accept the following arguments:
            - request: The request object.
            - meta: The ArcStackRequestMeta object.
            Should either return a new ArcStackRequestMeta object or None.
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
        self._endpoint_middleware = []
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

            if hasattr(mw_instance, 'process_endpoint'):
                self._endpoint_middleware.insert(0, mw_instance.process_endpoint)
            if hasattr(mw_instance, 'process_exception'):
                self._exception_middleware.append(mw_instance.process_exception)
        self._middleware_chain = handler

    def __call__(self, endpoint: Callable):
        return self._create_wrapper(endpoint)

    def _create_wrapper(self, endpoint: Callable):
        @wraps(endpoint)
        def wrapper(request, *args, **kwargs):
            request._arcstack_meta = ArcStackRequestMeta(endpoint, args, kwargs)

            try:
                response = self._middleware_chain(request)
            except Exception as e:
                response = self._process_exception(e, request)

            return response

        return wrapper

    def _get_response(self, request):
        if not hasattr(request, '_arcstack_meta'):
            raise ImproperlyConfigured(
                'The request object must have an `_arcstack_meta` attribute. '
                'To endpointify a view, use the `api_endpoint` decorator or '
                'subclass `Endpoint`.'
            )

        endpoint = request._arcstack_meta.endpoint
        args = request._arcstack_meta.args
        kwargs = request._arcstack_meta.kwargs
        del request._arcstack_meta

        response = None

        for middleware in self._endpoint_middleware:
            response = middleware(request, endpoint, *args, **kwargs)
            if response is not None:
                break

        if response is None:
            response = endpoint(request, *args, **kwargs)

        return response

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
