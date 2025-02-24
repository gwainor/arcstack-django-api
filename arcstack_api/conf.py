from django.conf import settings  # noqa

from appconf import AppConf


class ArcStackAPIConf(AppConf):
    DEFAULT_LOGIN_REQUIRED = False
    DEFAULT_CSRF_EXEMPT = True
    ERROR_RESPONSE_TEXTS = {
        401: 'Unauthorized',
        405: 'Method Not Allowed',
        500: 'Internal Server Error',
    }

    class Meta:
        prefix = 'api'
