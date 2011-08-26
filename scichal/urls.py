from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', 'scichal.reg.views.home'),
    (r'^paid/(?P<entrant_id>\d+)/$', 'scichal.reg.views.mark_paid'),
    (r'^email/$', 'scichal.reg.views.send_email'),
    (r'^accounts/login/$', 'django.contrib.auth.views.login'),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}),
    (r'^admin/', include(admin.site.urls)),
)
