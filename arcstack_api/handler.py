import logging

logger = logging.getLogger('arcstack_yapi.handler')


class APIHandler:
    _exception_middleware = None
    _middleware_chain = None

    def load_middleware(self):
        self._exception_middleware = []
