import json
from io import BytesIO

import pydantic
from django.http import HttpRequest
from django.utils.decorators import classonlymethod

from .conf import settings
from .constants import ALLOWED_HTTP_METHOD_NAMES, INVALID_INIT_KWARG_NAMES
from .encoders import ArcStackJSONEncoder
from .errors import HttpError, HttpMethodNotAllowedError
from .params.signature import EndpointSignature
from .responses import (
    ArcStackResponse,
    ErrorResponse,
    InternalServerErrorResponse,
    UnauthorizedResponse,
)
from .utils import is_accepted_pydantic_type


# isort: off


class ArcStackAPI:
    CSRF_EXEMPT = settings.API_DEFAULT_CSRF_EXEMPT
    LOGIN_REQUIRED = settings.API_DEFAULT_LOGIN_REQUIRED

    # Internal attributes
    # These cannot be used as init keyword arguments in `as_endpoint`
    http_method: str
    request: HttpRequest
    args: tuple
    kwargs: dict
    __signature__: EndpointSignature

    def __init__(self, signature: EndpointSignature, **kwargs):
        self.__signature__ = signature

        # Go through keyword arguments, and either save their values to our
        # instance, or raise an error.
        for key, value in kwargs.items():
            setattr(self, key, value)

    @classonlymethod
    def as_endpoint(cls, **initkwargs):
        cls._check_initkwargs(cls, initkwargs)

        signature = EndpointSignature(cls)

        def endpoint(request, *args, **kwargs):
            self = cls(signature, **initkwargs)

            if self.LOGIN_REQUIRED and not request.user.is_authenticated:
                return UnauthorizedResponse()

            response = ArcStackResponse({})

            self.setup(request, response, *args, **kwargs)

            if not hasattr(self, 'request'):
                if settings.DEBUG:
                    raise AttributeError(
                        f'`{cls.__name__}` instance has no `request` attribute. '
                        'Did you override `setup()` and forget to call `super()`?'
                    )
                else:
                    return InternalServerErrorResponse()

            return self.dispatch(response)

        endpoint.endpoint_class = cls
        endpoint.signature = signature

        # __name__ and __qualname__ are intentionally left unchanged as
        # endpoint_class should be used to robustly determine the name of the endpoint
        # instead.
        endpoint.__doc__ = cls.__doc__
        endpoint.__module__ = cls.__module__

        # Add csrf_exempt if the endpoint is csrf_exempt
        if cls.CSRF_EXEMPT:
            endpoint.__dict__.update({'csrf_exempt': True})

        return endpoint

    def setup(self, request: HttpRequest, response: ArcStackResponse, *args, **kwargs):
        self.request = request
        self.response = response
        self.args = args
        self.kwargs = kwargs

        self.http_method = self.request.method.lower()

        if self.http_method in ['post', 'put', 'patch']:
            if self.request.content_type == 'multipart/form-data':
                self.data, self.files = self.request.parse_file_upload(
                    self.request.META, BytesIO(self.request.body)
                )
                self.data = self.data.dict()
            else:
                self.data = json.loads(self.request.body)

    def dispatch(self, response: ArcStackResponse):
        try:
            if self.http_method not in self.__signature__.methods:
                raise HttpMethodNotAllowedError()

            method_kwargs = self._build_method_kwargs()

            endpoint_func = getattr(self, self.http_method)
            result = endpoint_func(**method_kwargs)

            result = self._process_result(result)

            response.content = json.dumps(result, cls=ArcStackJSONEncoder)
        except HttpError as e:
            response = ErrorResponse(str(e), status=e.status_code)
        except Exception as e:
            if settings.DEBUG:
                # If we're in debug mode, we want to see the full traceback
                # Let the Django server handle it
                raise e
            else:
                response = InternalServerErrorResponse()

        return response

    def _build_method_kwargs(self):
        """Build kwargs for the endpoint

        This method can be overridden.

        All requested arguments are extracted from the method signature using `inspect`.
        The `request` is being validated against requested HTTP method arguments.
        All arguments must be annotated with a pydantic model.
        """
        method_kwargs = self._method_signature.validate(self.request, self.kwargs)

        return method_kwargs

    def _process_result(self, result):
        if result is None:
            return None

        if self.http_method in ['head', 'trace', 'connect']:
            raise ValueError(
                f'`{self.__class__.__name__}.{self.http_method}` '
                'should not return a response body according to the HTTP spec.'
            )
        elif not is_accepted_pydantic_type(result):
            raise ValueError(
                f'`{self.__class__.__name__}.{self.http_method}` '
                'should return a `dict`, a `pydantic.BaseModel`, or `None`.'
            )

        if self._method_signature.return_annotation:
            result = self._method_signature.return_annotation.model_validate(result)

        if isinstance(result, pydantic.BaseModel):
            result = result.model_dump()

        return result

    @property
    def _method_signature(self):
        return self.__signature__.methods[self.http_method]

    def _check_initkwargs(cls, initkwargs):
        """Check the initkwargs for the endpoint

        This method can be overridden.
        """
        for key in initkwargs:
            if key in INVALID_INIT_KWARG_NAMES:
                raise TypeError(
                    f'The "{key}" keyword argument is reserved for internal use and '
                    'cannot be used as a keyword argument in API endpoints in '
                    f'`{cls.__name__}.as_endpoint()`.'
                )
            if key in ALLOWED_HTTP_METHOD_NAMES:
                raise TypeError(
                    f'The method name "{key}" is not accepted as a keyword argument '
                    f'to `{cls.__name__}.as_endpoint()`.'
                )
            if not hasattr(cls, key):
                raise TypeError(
                    f'`{cls.__name__}.as_endpoint()` received an invalid keyword "{key}". '
                    '`as_endpoint()` only accepts arguments that are already '
                    'attributes of the class.'
                )
