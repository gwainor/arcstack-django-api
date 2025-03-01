import logging

import pytest
from django.core.exceptions import ImproperlyConfigured, MiddlewareNotUsed

from arcstack_api.api import ArcStackAPI
from arcstack_api.logger import logger


def sample_middleware(get_response):
    raise MiddlewareNotUsed()


def sample_middleware_with_error_text(get_response):
    raise MiddlewareNotUsed('test')


def improperly_configured_middleware(get_response):
    return None


class MiddlewareWithProcessEndpoint:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_endpoint(self, request, endpoint, *args, **kwargs):
        return endpoint(request, *args, **kwargs)


class TestLoadMiddleware:
    def test_middleware_not_used(self, settings, caplog):
        settings.API_MIDDLEWARE = ['tests.test_arcstack_api.sample_middleware']

        api = ArcStackAPI()
        api.load_middleware()

        assert caplog.text == ''
        assert api._middleware_chain == api._get_response

    def test_middleware_not_used_with_debug(self, settings, caplog):
        settings.API_MIDDLEWARE = ['tests.test_arcstack_api.sample_middleware']
        settings.DEBUG = True
        logger.propagate = True

        with caplog.at_level(logging.DEBUG):
            api = ArcStackAPI()
            assert 'MiddlewareNotUsed' in caplog.text

        assert api._middleware_chain == api._get_response

    def test_middleware_not_used_with_error_text(self, settings, caplog):
        settings.API_MIDDLEWARE = [
            'tests.test_arcstack_api.sample_middleware_with_error_text'
        ]
        settings.DEBUG = True
        logger.propagate = True

        with caplog.at_level(logging.DEBUG):
            api = ArcStackAPI()
            assert 'MiddlewareNotUsed' in caplog.text
            assert 'test' in caplog.text

        assert api._middleware_chain == api._get_response

    def test_improperly_configured(self, settings):
        settings.API_MIDDLEWARE = [
            'tests.test_arcstack_api.improperly_configured_middleware'
        ]

        with pytest.raises(ImproperlyConfigured):
            ArcStackAPI()

    def test_get_response_without_request_meta(self, rf):
        api = ArcStackAPI()
        request = rf.get('/')
        with pytest.raises(ImproperlyConfigured):
            api._get_response(request)

    def test_process_endpoint_with_middleware(self, settings, rf):
        settings.API_MIDDLEWARE = [
            'tests.test_arcstack_api.MiddlewareWithProcessEndpoint'
        ]

        api = ArcStackAPI()

        assert len(api._endpoint_middleware) == 1


class TestProcessEndpoint:
    def test_process_endpoint(self, settings, rf):
        settings.API_MIDDLEWARE = []

        api = ArcStackAPI()

        def middleware(request, endpoint, *args, **kwargs):
            return 'test 2'

        api._endpoint_middleware = [middleware]

        @api
        def endpoint(request, *args, **kwargs):
            return 'test'

        request = rf.get('/')
        response = endpoint(request)
        assert response == 'test 2'


class TestProcessException:
    def test_unhandled_exception_returns_500(self, settings, rf, expect_response):
        settings.API_MIDDLEWARE = []

        api = ArcStackAPI()

        @api
        def endpoint(request, *args, **kwargs):
            raise ValueError('test')

        request = rf.get('/')
        response = endpoint(request)
        expect_response(response, status=500)

    def test_unhandled_exception_throws_in_debug_mode(self, settings, rf):
        settings.API_MIDDLEWARE = []
        settings.DEBUG = True

        api = ArcStackAPI()

        @api
        def endpoint(request, *args, **kwargs):
            raise ValueError('test')

        request = rf.get('/')
        with pytest.raises(ValueError):
            endpoint(request)

    def test_process_exception_with_middleware(self, settings, rf, expect_response):
        settings.API_MIDDLEWARE = []

        api = ArcStackAPI()

        def process_exception(exception, request):
            raise ValueError('test 2')

        api._exception_middleware = [process_exception]

        @api
        def endpoint(request, *args, **kwargs):
            raise ValueError('test')

        request = rf.get('/')
        response = endpoint(request)
        expect_response(response, status=500)
