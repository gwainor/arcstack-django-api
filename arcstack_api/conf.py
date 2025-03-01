from django.conf import settings  # noqa

from appconf import AppConf


class ArcStackAPIConf(AppConf):
    MIDDLEWARE = ['arcstack_api.middleware.CommonMiddleware']

    JSON_ENCODER = 'django.core.serializers.json.DjangoJSONEncoder'

    DEFAULT_LOGIN_REQUIRED = False

    class Meta:
        prefix = 'api'
