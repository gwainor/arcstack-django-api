def is_class_based_endpoint(endpoint):
    from .endpoint import Endpoint

    return isinstance(endpoint, type) and issubclass(endpoint, Endpoint)
