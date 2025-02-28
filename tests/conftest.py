import json
import os
import sys
from pathlib import Path

import pytest
from django.http import HttpResponse
from django.test import Client


ROOT = Path(__file__).parent.parent.resolve()

sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'tests/demo_project'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'demo.settings')

import django  # noqa

django.setup()


@pytest.fixture
def set_middleware(settings):
    def wrapper(middleware_list):
        from arcstack_api import arcstack_api

        settings.API_MIDDLEWARE = middleware_list
        arcstack_api.load_middleware()

    return wrapper


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def client_method(client):
    def wrapper(method_name, *args, **kwargs):
        method = getattr(client, method_name)

        if method_name in ['post', 'put', 'patch']:
            kwargs['content_type'] = 'application/json'
            if 'data' not in kwargs:
                kwargs['data'] = json.dumps({})
            elif isinstance(kwargs['data'], dict):
                kwargs['data'] = json.dumps(kwargs['data'])

        if 'user' in kwargs:
            client.force_login(kwargs['user'])
            del kwargs['user']

        return method(*args, **kwargs)

    return wrapper


@pytest.fixture
def expect_response():
    def wrapper(response: HttpResponse, status: int = 200, **kwargs):
        try:
            assert response.status_code == status
            if 'content_type' in kwargs:
                assert response.headers['Content-Type'] == kwargs['content_type']
            if 'content' in kwargs:
                assert response.content == kwargs['content']
        except AssertionError:
            # Useful for debugging
            print(response.content)
            raise

    return wrapper
