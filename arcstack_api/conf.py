from django.conf import settings  # noqa

from appconf import AppConf


class ArcStackAPIConf(AppConf):
    DEFAULT_LOGIN_REQUIRED = False
    DEFAULT_CSRF_EXEMPT = True

    class Meta:
        prefix = 'api'
