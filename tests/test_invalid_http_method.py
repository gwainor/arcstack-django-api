import pytest
from django.test import override_settings
from django.urls import path

from arcstack_api import ArcStackAPI


class Endpoint(ArcStackAPI):
    def get(self):
        return {'message': 'Hello, world!'}


urlpatterns = [
    path('api', Endpoint.as_endpoint()),
]


@override_settings(ROOT_URLCONF=__name__)
@pytest.mark.parametrize(
    'method_name, expected_status',
    [
        ('get', 200),
        ('post', 405),
        ('put', 405),
        ('patch', 405),
        ('delete', 405),
        ('options', 405),
        ('head', 405),
        ('trace', 405),
    ],
)
def test_invalid_http_method(
    client_method, expect_response, method_name, expected_status
):
    response = client_method(method_name, '/api')
    expect_response(response, status=expected_status)
