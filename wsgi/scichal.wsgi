import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'scichal.settings'

sys.path.append('/home/myrobogals/robogals')
sys.path.append('/home/myrobogals/robogals/scichal')
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
