# Middleware

This is the core of ArcStack Django API. The `Endpoint` is no different than
`View` class of Django without any middleware defined.

The middleware system is a shallow copy of the Django middleware system.
This is to ensure that when a new middleware needs to be created you don't
need to learn a complex system.

If you did not meddle into Django Middleware system yet, I suggest to read
its [documentation](https://docs.djangoproject.com/en/5.1/topics/http/middleware/) first.


> IMPORTANT: There is no `async` support yet.


## Defining Middleware

The middleware definiton can be changed in Django `settings`. The setting
variable name is `API_MIDDLEWARE`.

ArcStack Django API comes with following setting as default:

```py
API_MIDDLEWARE = [
    "arcstack_api.middleware.CommonMiddleware",
]
```


## Differences from Django Middleware

ArcStack API Middleware works same with Django middleware but there are
some differences that you need to be aware of.


### Request object

The ArcStack API defines a `_arcstack_meta` attribute to the incoming
`HttpRequest` object. This object stores the `endpoint` function and
`args` and `kwargs` passed from the Django.

Django, at the end of the middleware chain, resolves request to get the view
function and generates `args` and `kwargs` to pass to the view function.
These parameters are `path` parameters.

ArcStack API does not re-resolve requests since it is wasteful to do the same
operation twice. Instead, it generates a meta object to store the `view`
function, `args` and `kwargs` and attaches it to `request` object. This
`_arcstack_meta` object is removed from the `request` just before calling
`process_endpoint` and `endpoint` functions.


### Django middleware hooks

Django has some special hooks in the middleware system. For more information,
you can visit the [Django documentation](https://docs.djangoproject.com/en/5.1/topics/http/middleware/#other-middleware-hooks)


#### Use `process_endpoint` instead of `process_view`

[process_view()](https://docs.djangoproject.com/en/5.1/topics/http/middleware/#process-view)
middleware hook renamed to `process_endpoint` but behaves the same. This
hook especially useful if you want to have a functionality same as Django Ninja.


### No `process_template_response()` hook

[process_template_response()](https://docs.djangoproject.com/en/5.1/topics/http/middleware/#process-template-response)
hook has no use for API endpoints.