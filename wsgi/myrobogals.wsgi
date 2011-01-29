import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'myrobogals.settings'

sys.path.append('/var/home/myrobogals/robogals')
sys.path.append('/var/home/myrobogals/robogals/myrobogals')
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
