import json
from collections import namedtuple

import pytest
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse

from arcstack_api import APIError, Endpoint, api_endpoint, arcstack_api


Case = namedtuple('Case', ['return_type', 'return_value', 'expected_content'])
RESPONSE_CASES = [
    Case('str', 'Hello, World!', b'Hello, World!'),
    Case('int', 123, b'123'),
    Case('float', 123.456, b'123.456'),
    Case('bool', True, b'True'),
    Case('dict', {'key': 'value'}, b'{"key": "value"}'),
    Case('list', ['item1', 'item2', 'item3'], b'["item1", "item2", "item3"]'),
    Case('tuple', ('item1', 'item2', 'item3'), b'["item1", "item2", "item3"]'),
    Case('http_response', HttpResponse(content=b'Hello, World!'), b'Hello, World!'),
]


@pytest.fixture
def common_middleware(settings):
    old_middleware = settings.API_MIDDLEWARE
    settings.API_MIDDLEWARE = ['arcstack_api.middleware.common.CommonMiddleware']
    arcstack_api.load_middleware()

    yield

    settings.API_MIDDLEWARE = old_middleware
    arcstack_api.load_middleware()


class TestCommonMiddlewareResponseTransform:
    @pytest.mark.parametrize('case', RESPONSE_CASES)
    def test_responses(self, common_middleware, rf, case):
        class ApiEndpoint(Endpoint):
            def get(self, request, return_type: str):
                for case in RESPONSE_CASES:
                    if return_type == case.return_type:
                        return case.return_value
                else:
                    raise ValueError(f'Unsupported return type: {return_type}')

        endpoint = ApiEndpoint.as_endpoint()
        request = rf.get(f'/api/{case.return_type}')
        response = endpoint(request, return_type=case.return_type)
        assert response.status_code == 200
        assert response.content == case.expected_content


class TestCommonMiddlewareExceptionTransform:
    def test_exception(self, settings, common_middleware, rf, expect_response):
        settings.DEBUG = True

        class ApiEndpoint(Endpoint):
            def get(self, request):
                raise APIError('Test error')

        endpoint = ApiEndpoint.as_endpoint()
        request = rf.get('/api/exception')
        response = endpoint(request)
        expect_response(response, status=400, content_type='application/json')
        response_data = json.loads(response.content)
        assert response_data['error'] == 'Test error'
        assert response_data['status'] == 400


@pytest.mark.django_db
class TestCommonMiddlewareLoginRequired:
    def test_with_global_setting(
        self, settings, common_middleware, rf, expect_response, django_user_model
    ):
        settings.API_DEFAULT_LOGIN_REQUIRED = True

        class ApiEndpoint(Endpoint):
            def get(self, request):
                return 'Hello, World!'

        endpoint = ApiEndpoint.as_endpoint()
        request = rf.get('/api/login-required')
        request.user = AnonymousUser()
        response = endpoint(request)
        expect_response(response, status=401)

        request.user = django_user_model.objects.create_user(username='testuser')
        response = endpoint(request)
        expect_response(response, status=200, content=b'Hello, World!')

    def test_with_endpoint_setting(
        self, common_middleware, rf, expect_response, django_user_model
    ):
        class ApiEndpoint(Endpoint):
            LOGIN_REQUIRED = True

            def get(self, request):
                return 'Hello, World!'

        endpoint = ApiEndpoint.as_endpoint()
        request = rf.get('/api/login-required')
        request.user = AnonymousUser()
        response = endpoint(request)
        expect_response(response, status=401)

        request.user = django_user_model.objects.create_user(username='testuser')
        response = endpoint(request)
        expect_response(response, status=200, content=b'Hello, World!')

    def test_with_decorator(
        self, common_middleware, rf, expect_response, django_user_model
    ):
        @api_endpoint(login_required=True)
        def endpoint(request):
            return 'Hello, World!'

        request = rf.get('/api/login-required')
        request.user = AnonymousUser()
        response = endpoint(request)
        expect_response(response, status=401)

        request.user = django_user_model.objects.create_user(username='testuser')
        response = endpoint(request)
        expect_response(response, status=200, content=b'Hello, World!')
