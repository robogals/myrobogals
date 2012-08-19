from django.conf.urls.defaults import *
from django.contrib import admin
from scichal import settings

admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', 'scichal.reg.views.home'),
    (r'^paid/(?P<entrant_id>\d+)/$', 'scichal.reg.views.mark_paid'),
    (r'^email/$', 'scichal.reg.views.send_email'),
    (r'^accounts/login/$', 'django.contrib.auth.views.login'),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}),
    (r'^admin/', include(admin.site.urls)),
    (r'^scmedia/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT,}),
    (r'^adminmedia/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/var/lib/python-support/python2.5/django/contrib/admin/media/',}),
)
