import pytest
from django.test import override_settings
from django.urls import path
from pydantic import BaseModel, Field

from arcstack_api import ArcStackAPI, Query


def test_method_params(client_method, expect_response):
    class Endpoint(ArcStackAPI):
        def get(self, foo: str):
            return {'message': 'Hello, world!'}

    with pytest.raises(TypeError):
        Endpoint.as_endpoint()


def test_invalid_annotation_definition(client_method, expect_response):
    class Schema(BaseModel):
        foo: str

    class Endpoint(ArcStackAPI):
        def get(self, foo=Schema):
            return {'message': 'Hello, world!'}

    with pytest.raises(TypeError):
        Endpoint.as_endpoint()


class QuerySchema(BaseModel):
    foo: str = Field(max_length=3)


class QueryEndpoint(ArcStackAPI):
    def get(self, foo: Query[QuerySchema]):
        return {'message': 'Hello, world!'}


urlpatterns = [
    path('api', QueryEndpoint.as_endpoint()),
]


@override_settings(ROOT_URLCONF=__name__, DEBUG=True)
def test_query_endpoint(client_method, expect_response):
    response = client_method('get', '/api?foo=something_long')
    expect_response(response, status=400)
