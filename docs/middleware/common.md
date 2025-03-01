# Common Middleware

**Import string**: `arcstack_api.middleware.CommonMiddleware`

Common middleware is the most basic middleware that provides some functionality.

While it is not mandatory to use any middleware, it is strongly encouraged to
use the `CommonMiddleware`


## No HttpResponse return requirement

Django views always must return a `HttpResponse` object. The common middleware
checks your endpoint return and builds the `HttpResponse` object for you.


### `HttpResponse`

If the return is a `HttpRespose` object, nothing will be done.


### Basic types

`str`, `int`, `flaot`, `bool` types are converted to string and the content type
is set to `text/plain`.


### `list` and `dict`

`list` and `dict` objects are serialized to `json` and the content type is set
to `application/json`.


### Other types

If the object is serializable with `json` it will be serialized and the content
type will be set to `application/json`.

Any other type will result with a internal server error with status code `500`.


## Login Required check

The common middleware checks the `request.user` object if the endpoint is set
login required.

For class-based endpoints just define a class attribute called `LOGIN_REQUIRED`.

```py hl_lines="4"
from arcstack_api import Endpoint

class Sample(Endpoint):
    LOGIN_REQUIRED = True

    def get(self, request):
        return {"status": "OK"}
```

For function endpoints, you can define it in the decorator params:

```py hl_lines="3"
from arcstack_api import api_endpoint

@api_endpoint(login_required=True)
def sample(request):
    return {"status": "OK"}
```

For default, all enpoints are set to not login required but this behavior
can be change using `API_DEFAULT_LOGIN_REQUIRED` setting. The default is `False`.
If you set to `True` all endpoints will require a logged in user. You can still
set `login_required` to `False` on any endpoint to make it public.


## Early return with exceptions

Common middleware supports early returns with exceptions to return a HTTP `400`
error.

```py hl_lines="7"
from arcstack_api import APIError, Endpoint

class Sample(Endpoint):
    def get(self, request):
        ...
        if some_condition:
            raise APIError("Some condition is not met")
        
        return {"status": "OK"}
```

It is also possible to pass any other type like `list`, `dict` to `APIError`
to response as a `json`.


```py hl_lines="8"
from arcstack_api import APIError, Endpoint

class Sample(Endpoint):
    def get(self, request):
        ...
        if some_condition:
            raise APIError(
                {"error": "ugh. some condition has not met"},
                status_code=480, # (1)!
            )
        
        return {"status": "OK"}
```

1. Status code of the APIError is default to `400` but another response code
can be given.

There is also `UnauthorizedError` that can be raised if user is not authorized
to execute the endpoint

```py hl_lines="7"
from arcstack_api import Endpoint, UnauthorizedError

class Sample(Endpoint):
    def get(self, request):
        ...
        if some_condition:
            raise UnauthorizedError()
        
        return {"status": "OK"}
```

And lastly, there is `InternalServerError` if you want to trigger a `500` error
programmatically.