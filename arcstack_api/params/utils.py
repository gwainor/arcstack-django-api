import inspect
from collections.abc import Callable
from typing import Any, AnyStr, ForwardRef, cast


# isort: off


def get_typed_signature(call: Callable[..., Any]) -> inspect.Signature:
    """
    Finds call signature and resolves all forwardrefs
    These are taken from `django-ninja`
    """
    signature = inspect.signature(call)
    globalns = getattr(call, '__globals__', {})
    typed_params = [
        inspect.Parameter(
            name=param.name,
            kind=param.kind,
            default=param.default,
            annotation=get_typed_annotation(param, globalns),
        )
        for param in signature.parameters.values()
    ]
    typed_signature = inspect.Signature(typed_params)
    return typed_signature


def evaluate_forwardref(type_: ForwardRef, globalns: Any, localns: Any) -> Any:
    # Even though it is the right signature for python 3.9, mypy complains with
    # `error: Too many arguments for "_evaluate" of "ForwardRef"` hence the cast...
    return cast(Any, type_)._evaluate(globalns, localns, recursive_guard=set())


def make_forwardref(annotation: str, globalns: dict[AnyStr, Any]) -> Any:
    forward_ref = ForwardRef(annotation)
    return evaluate_forwardref(forward_ref, globalns, globalns)


def get_typed_annotation(param: inspect.Parameter, globalns: dict[AnyStr, Any]) -> Any:
    annotation = param.annotation
    if isinstance(annotation, str):
        annotation = make_forwardref(annotation, globalns)
    return annotation
