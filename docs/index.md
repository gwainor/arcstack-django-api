# ArcStack Django API - A REST Framework, Django way

ArcStack Django API is a framework that does not require any learning apart from
your Django knowledge.

Key Features:

- **Easy**: Uses Django URLs and Class Based Views.
- **Extensible**: Powerful middleware system just of API endpoints.
- **Same Context**: Does not require to change context like DRF.


## Installation

```sh
pip install arcstack-django-api
```


## Basic Usage

Create a file to store your API endpoints. `endpoints.py` is a good choice of name.
And create your first endpoint:

```py title="endpoints.py"
from arcstack_api import Endpoint


class StatusOk(Endpoint):
    def get(self, request):
        return {"status": "OK"} # (1)!
```

1.  Notice that return is not a `HttpResponse`. The ArcStack API checks your return
type and builds an appropriate `HttpResponse` object thanks to built-in
`CommonMiddleware`.

Now we have an endpoint, it is time to define the URL.

```python hl_lines="4 8" title="urls.py"
from django.contrib import admin
from django.urls import path

from . import endpoints

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", endpoints.StatusOk.as_endpoint()),
]
```

You need to use `.as_view()` in URL patterns When using Django class-based views.
The `Endpoint` structure is same but to differentiate the API endpoints from
normal views, you need to use `as_endpoint()`.

To keep the learning curve minimal, the `Endpoint` is extended from Django's
`View` class and the usage is same.