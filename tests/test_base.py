import json

import pytest
from django.test import Client


@pytest.mark.parametrize(
    'url',
    [
        '/api/simple',
        '/api/with-schema-returned',
        '/api/with-return-schema',
    ],
)
def test_schema_returned(url):
    client = Client()
    response = client.get(url)
    assert response.status_code == 200
    print(response.content)
    response_json = response.json()
    assert response_json == {'message': 'Hello, world!'}
    assert response.headers['Content-Type'] == 'application/json'


def test_path_param():
    client = Client()
    response = client.get('/api/with-path-param/John')
    assert response.status_code == 200
    assert response.json() == {'who': 'John'}


def test_login_required():
    client = Client()
    response = client.get('/api/with-login-required')
    assert response.status_code == 401


def test_body():
    client = Client()
    message = {'message': 'Hello, world!'}
    response = client.post(
        '/api/with-body', content_type='application/json', data=json.dumps(message)
    )
    assert response.status_code == 200
    assert response.json() == message


def test_api_error():
    client = Client()
    response = client.get('/api/with-api-error')
    assert response.status_code == 400
    assert response.json() == {'error': 'Interrupted with APIError'}
