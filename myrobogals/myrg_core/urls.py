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
)
