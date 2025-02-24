import pytest

from arcstack_api import ArcStackAPI


class Endpoint(ArcStackAPI):
    foo: str = None
    foo2: str

    def get(self):
        return {'message': 'Hello, world!'}


def test_initkwargs_with_existing_attribute():
    # Should not raise an error
    Endpoint.as_endpoint(foo='bar')


def test_initkwargs_with_not_existing_attribute():
    with pytest.raises(TypeError):
        # Should still raise an error because foo2 has not been initialized
        # with a default value
        Endpoint.as_endpoint(foo2='bar')

    with pytest.raises(TypeError):
        Endpoint.as_endpoint(foo3='bar')


@pytest.mark.parametrize(
    'arg_name',
    ['request', 'args', 'kwargs', '__signature__', 'http_method', 'response'],
)
def test_initkwargs_with_invalid_arg_name(arg_name):
    with pytest.raises(TypeError):
        Endpoint.as_endpoint(**{arg_name: 'bar'})


@pytest.mark.parametrize(
    'method_name',
    ['get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'trace'],
)
def test_initkwargs_with_invalid_method_name(method_name):
    with pytest.raises(TypeError):
        Endpoint.as_endpoint(**{method_name: 'bar'})
