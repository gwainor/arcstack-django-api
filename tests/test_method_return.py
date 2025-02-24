import json

import pytest
from django.test import override_settings
from django.urls import path
from pydantic import BaseModel

from arcstack_api import ArcStackAPI, Body


# isort: off


class Schema(BaseModel):
    return_type: str | None = None


class Endpoint(ArcStackAPI):
    def post(self, body: Body[Schema]):
        if body.return_type == 'dict':
            return {'message': 'Hello, world!'}
        elif body.return_type == 'str':
            return 'Hello, world!'
        elif body.return_type == 'list':
            return [1, 2, 3]
        elif body.return_type == 'schema':
            return Schema(return_type='sample')
        else:
            return None

    def put(self, body: Body[Schema]) -> Schema:
        if body.return_type == 'valid':
            return {'return_type': 'sample'}
        elif body.return_type == 'invalid':
            # Schema expects `str`, but `int` is returned
            # This should raise a validation error
            return {'return_type': 1}


urlpatterns = [
    path('api', Endpoint.as_endpoint()),
]


@pytest.fixture
def make_request(client_method):
    def wrapper(return_type=None):
        data = {'return_type': return_type}
        return client_method('post', '/api', data=json.dumps(data))

    return wrapper


class TestMethodReturnTypes:
    @override_settings(ROOT_URLCONF=__name__)
    def test_return_none__valid(self, make_request, expect_response):
        response = make_request()
        expect_response(response, status=200)

    @override_settings(ROOT_URLCONF=__name__)
    def test_return_dict__valid(self, make_request, expect_response):
        response = make_request('dict')
        expect_response(response, status=200)
        assert response.json() == {'message': 'Hello, world!'}

    @override_settings(ROOT_URLCONF=__name__)
    def test_return_str_without_debug_mode__invalid(
        self, make_request, expect_response
    ):
        response = make_request('str')
        expect_response(response, status=500)

    @override_settings(ROOT_URLCONF=__name__, DEBUG=True)
    def test_return_str_with_debug_mode__invalid(self, make_request):
        with pytest.raises(ValueError):
            make_request('str')

    @override_settings(ROOT_URLCONF=__name__)
    def test_return_schema__valid(self, make_request, expect_response):
        response = make_request('schema')
        expect_response(response, status=200)
        assert response.json() == {'return_type': 'sample'}


class TestMethodReturnAnnotations:
    @override_settings(ROOT_URLCONF=__name__)
    def test_return_annotation__valid(self, client_method, expect_response):
        response = client_method(
            'put', '/api', data=json.dumps({'return_type': 'valid'})
        )
        expect_response(response, status=200)
        assert response.json() == {'return_type': 'sample'}

    @override_settings(ROOT_URLCONF=__name__)
    def test_return_annotation__invalid(self, client_method, expect_response):
        response = client_method(
            'put', '/api', data=json.dumps({'return_type': 'invalid'})
        )
        expect_response(response, status=500)
