from asgiref.sync import markcoroutinefunction
from django.utils.decorators import classonlymethod
from django.views import View

from .api import arcstack_api
from .conf import settings
from .responses import MethodNotAllowedResponse, NotFoundResponse


class Endpoint(View):
    @classonlymethod
    def as_endpoint(cls, **initkwargs):
        """Serve the view as an endpoint.

        The `View` class is a base class for all Django class-based views.
        """
        for key in initkwargs:
            if key in cls.http_method_names:
                raise TypeError(
                    f'The method name {key} is not accepted as a keyword argument '
                    f'to {cls.__name__}().'
                )
            if not hasattr(cls, key):
                raise TypeError(
                    f'{cls.__name__}() received an invalid keyword {key}. '
                    'as_endpoint only accepts arguments that are already '
                    'attributes of the class.'
                )

        def endpoint(request, *args, **kwargs):
            self = cls(**initkwargs)
            self.http_method = request.method.lower()

            if 'setup_kwargs' in kwargs:
                self.setup(request, **kwargs['setup_kwargs'])
                del kwargs['setup_kwargs']
            else:
                self.setup(request, *args, **kwargs)

            if self.http_method not in self.http_method_names:
                return MethodNotAllowedResponse()

            return self.dispatch(request, *args, **kwargs)

        endpoint.view_class = cls
        endpoint.view_initkwargs = initkwargs

        # __name__ and __qualname__ are intentionally left unchanged as
        # view_class should be used to robustly determine the name of the view
        # instead.
        endpoint.__doc__ = cls.__doc__
        endpoint.__module__ = cls.__module__
        endpoint.__annotations__ = cls.dispatch.__annotations__
        # Copy possible attributes set by decorators, e.g. @csrf_exempt, from
        # the dispatch method.
        endpoint.__dict__.update(cls.dispatch.__dict__)

        # Mark the callback if the view class is async.
        if cls.view_is_async:
            markcoroutinefunction(endpoint)

        endpoint.LOGIN_REQUIRED = getattr(
            cls, 'LOGIN_REQUIRED', settings.API_DEFAULT_LOGIN_REQUIRED
        )

        return arcstack_api(endpoint)

    def setup(self, request, *args, **kwargs):
        pass

    def dispatch(self, request, *args, **kwargs):
        handler = getattr(self, self.http_method, None)

        if handler is None:
            return NotFoundResponse()

        if 'method_args' in kwargs:
            return handler(**kwargs['method_args'])
        else:
            return handler(request, *args, **kwargs)
