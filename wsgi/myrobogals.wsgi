import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'myrobogals.settings'

sys.path.append('/home/myrobogals/robogals')
sys.path.append('/home/myrobogals/robogals/myrobogals')
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
