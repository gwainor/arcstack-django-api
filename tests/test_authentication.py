import pytest
from django.contrib.auth.models import User
from django.test import override_settings
from django.urls import path

from arcstack_api import ArcStackAPI


class Endpoint(ArcStackAPI):
    LOGIN_REQUIRED = True

    def get(self):
        return {'message': 'Hello, world!'}


urlpatterns = [
    path('api', Endpoint.as_endpoint()),
]


@pytest.mark.django_db
class TestLoginRequired:
    @override_settings(ROOT_URLCONF=__name__)
    def test_annonymous_user_should_receive_401(self, client_method, expect_response):
        response = client_method('get', '/api')
        expect_response(response, status=401)

    @override_settings(ROOT_URLCONF=__name__)
    def test_authenticated_user_should_receive_200(
        self, client_method, expect_response
    ):
        user = User.objects.create_user(username='test')
        response = client_method('get', '/api', user=user)
        expect_response(response, status=200)
