import pytest
from django.http import HttpResponse

from arcstack_api import Endpoint, api


@pytest.fixture
def empty_middleware(settings):
    old_middleware = settings.API_MIDDLEWARE
    settings.API_MIDDLEWARE = []
    api.load_middleware()
    yield
    settings.API_MIDDLEWARE = old_middleware
    api.load_middleware()


class TestBareEndpoint:
    """Tests that the bare endpoint returns a 200 status code and 'Hello, world!' content.

    In the empty middleware chain, it is no different than a regular Django View.
    """

    def test_class_based_endpoint(self, empty_middleware, rf, expect_response):
        class BareEndpoint(Endpoint):
            def get(self, *args, **kwargs):
                return HttpResponse(status=200, content=b'Hello, world!')

        endpoint = BareEndpoint.as_endpoint()
        request = rf.get('/api')
        response = endpoint(request)
        expect_response(response, status=200, content=b'Hello, world!')

    def test_function_based_endpoint(self, empty_middleware, rf, expect_response):
        @api
        def endpoint(*args, **kwargs):
            return HttpResponse(status=200, content=b'Hello, world!')

        request = rf.get('/api')
        response = endpoint(request)
        expect_response(response, status=200, content=b'Hello, world!')

    def test_no_http_response(self, empty_middleware, rf):
        """This would fail on a regular Django flow because the view would return a string."""

        @api
        def endpoint(*args, **kwargs):
            return 'Hello, world!'

        request = rf.get('/api')
        response = endpoint(request)
        assert not isinstance(response, HttpResponse)
        assert response == 'Hello, world!'

    def test_errored_endpoint_returns_500_in_production(
        self, empty_middleware, rf, expect_response
    ):
        @api
        def endpoint(*args, **kwargs):
            raise Exception('Test exception')

        request = rf.get('/api')
        response = endpoint(request)
        expect_response(response, status=500)

    def test_errored_endpoint_trows_in_development(
        self, settings, empty_middleware, rf, expect_response
    ):
        settings.DEBUG = True

        @api
        def endpoint(*args, **kwargs):
            raise Exception('Test exception')

        request = rf.get('/api')
        with pytest.raises(Exception):  # noqa
            endpoint(request)
