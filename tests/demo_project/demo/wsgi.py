import os
import sys

from django.core.wsgi import get_wsgi_application


sys.path.insert(0, '../../')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'demo.settings')

application = get_wsgi_application()
