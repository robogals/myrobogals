from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.models import Group
from myrg_users.models import RobogalsUser

from rest_framework import viewsets, routers

from myrg_users.views import RobogalsUserViewSet, GroupViewSet
from myrg_message.views import MessageViewSet, MessageDefinitionViewSet
from myrg_groups.views import RoleTypeViewSet, RoleViewSet


############# Django REST Framework ###############
api_router = routers.DefaultRouter()
api_router.register(r'users', RobogalsUserViewSet)
api_router.register(r'groups', GroupViewSet)
api_router.register(r'message', MessageViewSet)
api_router.register(r'messagedefinition', MessageDefinitionViewSet)
api_router.register(r'roletype', RoleTypeViewSet)
api_router.register(r'role', RoleViewSet)
####################################################

# Auto generate/collate Django admin panels
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'myrobogals.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),

    # Django REST Framework
    url(r'^api/1.0/message/send.json/', 'myrg_message.views.send_message'),
    url(r'^api/1.0/', include(api_router.urls)),
    url(r'^api/auth/', include('rest_framework.urls', namespace='rest_framework')),
    
    # OAuth Django Toolkit
    url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
)
