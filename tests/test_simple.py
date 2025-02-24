"""Tests the endpoints without pydantic models."""

import json

import pytest
from django.test import override_settings
from django.urls import path

from arcstack_api import APIError, ArcStackAPI


RESPONSE = {'message': 'Hello, world!'}


class Simple(ArcStackAPI):
    should_raise = False

    def get(self):
        if self.should_raise:
            raise APIError('test error')
        return RESPONSE

    def post(self):
        if self.should_raise:
            raise APIError(self.data['message'])
        return self.data

    def put(self):
        if self.should_raise:
            raise APIError(self.data['message'])
        return self.data

    def patch(self):
        if self.should_raise:
            raise APIError(self.data['message'])
        return self.data

    def delete(self):
        if self.should_raise:
            raise APIError('test error')
        return RESPONSE

    def options(self):
        if self.should_raise:
            raise APIError('test error')
        return RESPONSE


urlpatterns = [
    path('api', Simple.as_endpoint()),
    path('api/error', Simple.as_endpoint(should_raise=True)),
    path('api/login-required', Simple.as_endpoint(LOGIN_REQUIRED=True)),
]


@override_settings(ROOT_URLCONF=__name__)
@pytest.mark.parametrize(
    'method_name', ['get', 'post', 'put', 'patch', 'delete', 'options']
)
def test_simple(client_method, expect_response, method_name):
    # Add a data argument for POST, PUT, and PATCH requests
    if method_name in ['post', 'put', 'patch']:
        expected_response = {'message': 'request with body data'}
        client_kwargs = {
            'data': json.dumps(expected_response),
        }
    else:
        client_kwargs = {}
        expected_response = RESPONSE

    response = client_method(method_name, '/api', **client_kwargs)
    expect_response(response)
    assert response.json() == expected_response


@override_settings(ROOT_URLCONF=__name__)
@pytest.mark.parametrize(
    'method_name', ['get', 'post', 'put', 'patch', 'delete', 'options']
)
def test_simple_error(client_method, expect_response, method_name):
    if method_name in ['post', 'put', 'patch']:
        expected_response_text = 'test error with body data'
        client_kwargs = {
            'data': json.dumps({'message': expected_response_text}),
        }
    else:
        expected_response_text = 'test error'
        client_kwargs = {}

    response = client_method(method_name, '/api/error', **client_kwargs)
    expect_response(response, status=400)
    assert response.json() == {'error': expected_response_text}


@override_settings(ROOT_URLCONF=__name__)
def test_login_required(client_method, expect_response):
    response = client_method('get', '/api/login-required')
    expect_response(response, status=401)
