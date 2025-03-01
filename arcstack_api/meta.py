from collections.abc import Callable

from .signature import EndpointSignature


class ArcStackRequestMeta:
    endpoint: Callable
    args: tuple
    kwargs: dict
    _signature: EndpointSignature = None

    def __init__(self, endpoint: Callable, args: tuple, kwargs: dict):
        self.endpoint = endpoint
        self.args = args
        self.kwargs = kwargs

    @property
    def signature(self) -> EndpointSignature:
        """Lazy signature creation."""
        if self._signature is None:
            self._signature = EndpointSignature(self.endpoint)
        return self._signature
