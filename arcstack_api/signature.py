import inspect
from collections import namedtuple
from collections.abc import Callable


# isort: off


MethodSignature = namedtuple(
    'MethodSignature', ['name', 'signature', 'params', 'return_annotation']
)


class EndpointSignature:
    def __init__(self, endpoint: Callable):
        # `view_class` is a special attribute that Django sets for class-based views.
        endpoint_cls = getattr(endpoint, 'view_class', None)
        self.is_class_based = endpoint_cls is not None

        self.signature = inspect.signature(endpoint_cls or endpoint)
