from django.utils.decorators import classonlymethod
from django.views import View

from .api import api


class Endpoint(View):
    @classonlymethod
    def as_endpoint(cls, **initkwargs):
        """Serve the view as an endpoint.

        The `View` class is a base class for all Django class-based views.
        """
        return api(super().as_view(**initkwargs))
