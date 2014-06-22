from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.models import Group
from myrg_users.models import RobogalsUser

from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns

# from myrg_users.views import RobogalsUserViewSet, GroupViewSet
from myrg_users.views import ListUsers


############# Django REST Framework ###############
# api_router = DefaultRouter()
# api_router.register(r'users', RobogalsUserViewSet, 'user')
# api_router.register(r'groups', GroupViewSet, 'group')
####################################################

# Auto generate/collate Django admin panels
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'myrobogals.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),

    # Django REST Framework
    #url(r'^api/1.0/', include(api_router.urls)),
    url(r'^api/auth/', include('rest_framework.urls', namespace='rest_framework')),
    
    # OAuth Django Toolkit
    url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
)

api_urlpatterns = patterns('',
    url(r'^api/1.0/users/list$', ListUsers.as_view()),
)

api_urlpatterns = format_suffix_patterns(api_urlpatterns, allowed=['json'])

urlpatterns += api_urlpatterns


