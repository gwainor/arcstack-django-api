class MiddlewareMixin:
    def __init__(self, get_response):
        if get_response is None:
            raise ValueError('get_response must be provided.')
        self.get_response = get_response

    def __repr__(self):
        qualname = self.__class__.__qualname__
        get_response_qualname = getattr(
            self.get_response,
            '__qualname__',
            self.get_response.__class__.__name__,
        )
        return f'<{qualname} get_response={get_response_qualname}>'

    def __call__(self, request, *args, **kwargs):
        response = None

        if hasattr(self, 'process_request'):
            response = self.process_request(request, *args, **kwargs)

        response = response or self.get_response(request, *args, **kwargs)

        if hasattr(self, 'process_response'):
            response = self.process_response(request, response, *args, **kwargs)

        return response
