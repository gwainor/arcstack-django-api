import inspect
from collections.abc import Callable
from typing import Any


# isort: off


def get_typed_signature(call: Callable[..., Any]) -> tuple[inspect.Signature, Any]:
    """
    Finds call signature and resolves all forwardrefs
    These are taken from `django-ninja`
    """
    signature = inspect.signature(call)
    typed_params = [
        inspect.Parameter(
            name=param.name,
            kind=param.kind,
            default=param.default,
            annotation=param.annotation,
        )
        for param in signature.parameters.values()
    ]
    typed_signature = inspect.Signature(
        typed_params,
        return_annotation=signature.return_annotation,
    )

    return typed_signature
