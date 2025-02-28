from collections.abc import Callable

from .api import arcstack_api
from .conf import settings


class api_endpoint:
    def __init__(
        self,
        login_required: bool = settings.API_DEFAULT_LOGIN_REQUIRED,
        *args,
        **kwargs,
    ):
        self.login_required = login_required

    def __call__(self, endpoint: Callable):
        endpoint.LOGIN_REQUIRED = self.login_required
        return arcstack_api._create_wrapper(endpoint)
