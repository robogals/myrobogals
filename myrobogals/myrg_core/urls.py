from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.models import Group
from myrg_users.models import RobogalsUser

from rest_framework import viewsets, routers

from myrg_users import views


############# Django REST Framework ###############
api_router = routers.DefaultRouter()
api_router.register(r'users', views.RobogalsUserViewSet)
api_router.register(r'groups', views.GroupViewSet)
####################################################

# Auto generate/collate Django admin panels
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'myrobogals.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),

    # Django REST Framework
    url(r'^api/1.0/', include(api_router.urls)),
    url(r'^api/auth/', include('rest_framework.urls', namespace='rest_framework')),

    # OAuth Django Toolkit
    url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
)

urlpatterns += patterns(
    'django.contrib.auth.views',
    url(r'^password-change/done/$', 'password_change_done', name='password_change_done'),
    url(r'^password-reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        'password_reset_confirm',
        name='password_reset_confirm'),
    url(r'^password-reset/done/$',
        'password_reset_done',
        name='password_reset_done'),
    url(r'^password-reset/complete/$',
        'password_reset_complete',
        name='password_reset_complete'),
)
 
