# ArcStack Django API Framework

[![Tests](https://github.com/gwainor/arcstack-django-api/actions/workflows/test.yml/badge.svg?branch=master&event=push)](https://github.com/gwainor/arcstack-django-api/actions/workflows/test.yml)

This is a simple yet extensible API framework for Django that you can create API
endpoints Django way.

Check out [Documentation](https://gwainor.github.io/arcstack-django-api/) for
more info.


## Sponsoring

Maintaining an open-source project requires attention and time. If you like this
project and want it to be developed further, you might want to consider giving
me a support.

If you are using ArcStack API in your project, please give me your feedback at
[me@gokhan.tr](mailto:me@gokhan.tr).


## Installation

```sh
pip install arcstack-django-api
```


## Usage

ArcStack Django API comes with `CommonMiddleware` enabled. This middleware
can convert your endpoint results to `HttpResponse`, handle exceptions and
check for logged in users.

Usage with class-based views:

```python
from arcstack_api import Endpoint, APIError

class StatusOk(Endpoint):
    # By default all defined enpoints do not require logged in user
    # You can change this behavior with this class constant.
    LOGIN_REQUIRED = True

    def get(self, request, a: str | None = None):
        if a == "something_invalid":
            # This `dict` will be converted to `JSON` and `HttpResponse`
            # will be generated
            raise APIError(
                {"error": "you have passed invalid argument"}
                # The default status_code is `400` but it can be changed to
                # anything you want.
                status_code=480
            )

        # ArcStack API will serialize this to JSON and generate
        # a `HttpResponse` for you.
        return {"status": "OK"}
```

Usage with function views:

```python
from arcstack_api import api_endpoint, Endpoint, APIError

@api_endpoint(login_required=True)
def statusOk(request, a: str | None = None):
    if a == "something_invalid":
        raise APIError(
            {"error": "you have passed invalid argument"}
            status_code=480
        )

    return {"status": "OK"}
```

In `urls.py`

```python
from django.urls import path

from . import endpoints

urlpatterns = [
    # For class-based views:
    path("api", endpoints.StatusOk.as_endpoint()),
    # For function views:
    path("api", endpoints.statusOk),
]
```
