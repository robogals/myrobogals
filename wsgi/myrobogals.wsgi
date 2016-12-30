import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'myrobogals.settings'
sys.path.append('/home/ubuntu/robogals/myrobogals')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
