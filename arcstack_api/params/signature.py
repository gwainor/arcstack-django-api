import inspect
from collections.abc import Callable
from dataclasses import dataclass
from typing import Annotated, Any, get_args, get_origin

import pydantic
from django.http import HttpRequest

from ..constants import ALLOWED_HTTP_METHODS
from ..errors import ValidationError
from .models import Param
from .utils import get_typed_signature


# isort: off


@dataclass
class MethodParam:
    name: str
    param_type: Param
    schema: pydantic.BaseModel

    def validate(self, request: HttpRequest, path: dict[str, Any]) -> Any:
        data = self.param_type.get_request_data(request, path)
        return self.schema.model_validate(data)


class MethodSignature:
    name: str
    signature: inspect.Signature
    params: list[MethodParam]
    response_schema: pydantic.BaseModel | None = None

    def __init__(self, name: str, method: Callable[..., Any]) -> None:
        self.name = name
        self.signature = get_typed_signature(method)
        self.params = []

        return_annotation = self.signature.return_annotation
        if return_annotation is not inspect.Parameter.empty and isinstance(
            return_annotation, pydantic.BaseModel
        ):
            self.response_schema = return_annotation

        for name, arg in self.signature.parameters.items():
            if name == 'self':
                # skipping `self`
                continue

            if arg.kind == arg.VAR_KEYWORD:
                # skipping **kwargs
                continue

            if arg.kind == arg.VAR_POSITIONAL:
                # skipping *args
                continue

            if (
                arg.annotation is inspect.Parameter.empty
                and isinstance(arg.default, type)
                and issubclass(arg.default, pydantic.BaseModel)
            ):
                raise ValueError(
                    f'Looks like you are using `{name}={arg.default.__name__}` '
                    f'instead of `{name}: {arg.default.__name__}` (annotation)'
                )

            if get_origin(arg.annotation) is not Annotated:
                raise ValueError(
                    f'Invalid annotation for parameter `{name}`: `{arg.annotation}`, '
                    'You need to use one of the `Param` types provided by the `arcstack_api`.'
                )

            schema, param_type = get_args(arg.annotation)
            self.params.append(MethodParam(name, param_type, schema))

    def validate(self, request: HttpRequest, path: dict[str, Any]) -> dict[str, Any]:
        exceptions = []
        params = {}
        for param in self.params:
            try:
                params[param.name] = param.validate(request, path)
            except pydantic.ValidationError as e:
                exceptions.append(e)

        if exceptions:
            raise ValidationError(exceptions)

        return params


class EndpointSignature:
    endpoint: Callable[..., Any]
    methods: dict[str, MethodSignature]

    def __init__(self, endpoint: Callable[..., Any]):
        self.endpoint = endpoint
        self.methods = {
            method: MethodSignature(method, getattr(endpoint, method))
            for method in ALLOWED_HTTP_METHODS
            if hasattr(endpoint, method)
        }
