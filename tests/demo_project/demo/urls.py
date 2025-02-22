from django.urls import include, path

from . import endpoints


apipatterns = [
    path('simple', endpoints.SimpleEndpoint.as_endpoint()),
    path('with-return-schema', endpoints.WithReturnSchema.as_endpoint()),
    path('with-schema-returned', endpoints.WithSchemaReturned.as_endpoint()),
    path('with-path-param/<str:who>', endpoints.WithPathParam.as_endpoint()),
    path('with-login-required', endpoints.WithLoginRequired.as_endpoint()),
    path('with-body', endpoints.WithBody.as_endpoint()),
    path('with-api-error', endpoints.WithAPIError.as_endpoint()),
]


urlpatterns = [
    path('api/', include(apipatterns)),
]
