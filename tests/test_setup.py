import pytest
from django.test import override_settings
from django.urls import path

from arcstack_api import ArcStackAPI


# isort: off


class Endpoint(ArcStackAPI):
    should_setup_call_super = False
    head_returns_body = False

    def setup(self, request, response, *args, **kwargs):
        if self.should_setup_call_super:
            super().setup(request, response, *args, **kwargs)

    def get(self, *args, **kwargs):
        return {'message': 'Hello, world!'}


urlpatterns = [
    path('api', Endpoint.as_endpoint()),
]


class TestMissingSuperSetup:
    @override_settings(ROOT_URLCONF=__name__, DEBUG=True)
    def test_missing_super_setup_raises_attribute_error(self, client_method):
        with pytest.raises(AttributeError):
            client_method('get', '/api')

    @override_settings(ROOT_URLCONF=__name__, DEBUG=False)
    def test_missing_super_setup_returns_internal_server_error(
        self, client_method, expect_response
    ):
        response = client_method('get', '/api')
        expect_response(response, status=500)
