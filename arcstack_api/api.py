import json
from io import BytesIO

import pydantic
from django.http import HttpRequest
from django.utils.decorators import classonlymethod

from .conf import settings
from .encoders import ArcStackJSONEncoder
from .errors import ArcStackError, ValidationError
from .params.signature import EndpointSignature
from .responses import (
    ArcStackResponse,
    HttpMethodNotAllowedResponse,
    UnauthorizedResponse,
    ValidationErrorResponse,
)


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
        _check_initkwargs(cls, initkwargs)

        signature = EndpointSignature(cls)

        def endpoint(request, *args, **kwargs):
            self = cls(signature, **initkwargs)

            if cls.LOGIN_REQUIRED and not request.user.is_authenticated:
                return UnauthorizedResponse()

            response = ArcStackResponse({})

            self.setup(request, response, *args, **kwargs)

            if self.request is None:
                raise AttributeError(
                    f'{cls.__name__} instance has no "request" attribute. Did you override '
                    'setup() and forget to call super()?'
                )

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
        if self.http_method not in self.__signature__.methods:
            return HttpMethodNotAllowedResponse()

        method_signature = self.__signature__.methods[self.http_method]
        # Build kwargs for the endpoint
        try:
            method_kwargs = method_signature.validate(self.request, self.kwargs)
        except ValidationError as e:
            return ValidationErrorResponse(e.errors)

        endpoint_func = getattr(self, self.http_method)

        try:
            result = endpoint_func(**method_kwargs)

            if method_signature.response_schema:
                result = method_signature.response_schema.model_validate(result)

            if isinstance(result, pydantic.BaseModel):
                result = result.model_dump()
            elif not isinstance(result, dict) and not isinstance(result, list):
                raise ValueError(
                    f'Invalid return type: {type(result)}. '
                    'Must be a dict, a pydantic.BaseModel, or None.'
                )

            response.content = json.dumps(result, cls=ArcStackJSONEncoder)
            return response
        except (ArcStackError, pydantic.ValidationError) as e:
            msg = str(e) if isinstance(e, ArcStackError) else e
            return ValidationErrorResponse(msg)

    @property
    def _allowed_methods(self):
        return [m.upper() for m in self.http_method_names if hasattr(self, m)]


def _check_initkwargs(cls, initkwargs):
    for key in initkwargs:
        if key in [
            'request',
            'args',
            'kwargs',
            '__signature__',
            'http_method',
            'response',
        ]:
            raise TypeError(
                f'The {key} keyword argument is reserved for internal use and '
                'cannot be used as a keyword argument in API endpoints.'
            )
        if key in cls.http_method_names:
            raise TypeError(
                f'The method name {key} is not accepted as a keyword argument '
                f'to {cls.__name__}().'
            )
        if not hasattr(cls, key):
            raise TypeError(
                f'{cls.__name__}() received an invalid keyword {key}. as_endpoint '
                'only accepts arguments that are already '
                'attributes of the class.'
            )
