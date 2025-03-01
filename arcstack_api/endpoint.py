from django.utils.decorators import classonlymethod
from django.views import View

from .api import arcstack_api


class Endpoint(View):
    @classonlymethod
    def as_endpoint(cls, **initkwargs):
        return arcstack_api(cls.as_view(**initkwargs))
