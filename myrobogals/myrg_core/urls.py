from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.models import Group
from myrg_users.models import RobogalsUser

from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns


from myrg_core.views import Time
from myrg_users.views import ListUsers, DeleteUsers, EditUsers, CreateUsers, ResetUserPasswords, WhoAmI, ListMyRoles, KillSessions
from myrg_groups.views import ListGroups, DeleteGroups, EditGroups, CreateGroups, ListRoles, EditRoles, CreateRoles, ListRoleClasses, DeleteRoleClasses, EditRoleClasses, CreateRoleClasses 

from myrg_webapp.views import WebApp

# Auto generate/collate Django admin panels
admin.autodiscover()
admin.site.unregister(Group)

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),

    # Django REST Framework
    url(r'^api/auth/', include('rest_framework.urls', namespace='rest_framework')),
    
    # OAuth Django Toolkit
    url(r'^api/o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
)

# API 1.0
api_urlpatterns = patterns('',
    url(r'^api/1.0/utils/time$', Time.as_view()),
    url(r'^api/1.0/utils/pwdreset/initiate$', ResetUserPasswords.as_view()),
    #url(r'^api/1.0/utils/pwdreset/complete', SetUserPasswords.as_view()),
    
    url(r'^api/1.0/users/list$', ListUsers.as_view()),
    url(r'^api/1.0/users/delete$', DeleteUsers.as_view()),
    url(r'^api/1.0/users/edit$', EditUsers.as_view()),
    url(r'^api/1.0/users/create$', CreateUsers.as_view()),
    
    url(r'^api/1.0/self/whoami$', WhoAmI.as_view()),
    url(r'^api/1.0/self/roles$', ListMyRoles.as_view()),
    url(r'^api/1.0/self/killsessions$', KillSessions.as_view()),
                           
    url(r'^api/1.0/groups/list$', ListGroups.as_view()),
    url(r'^api/1.0/groups/delete$', DeleteGroups.as_view()),
    url(r'^api/1.0/groups/edit$', EditGroups.as_view()),
    url(r'^api/1.0/groups/create$', CreateGroups.as_view()),
    
    url(r'^api/1.0/roles/list$', ListRoles.as_view()),
    url(r'^api/1.0/roles/edit$', EditRoles.as_view()),
    url(r'^api/1.0/roles/create$', CreateRoles.as_view()),
    
    url(r'^api/1.0/roleclasses/list$', ListRoleClasses.as_view()),
    url(r'^api/1.0/roleclasses/delete$', DeleteRoleClasses.as_view()),
    url(r'^api/1.0/roleclasses/edit$', EditRoleClasses.as_view()),
    url(r'^api/1.0/roleclasses/create$', CreateRoleClasses.as_view()),
)

api_urlpatterns = format_suffix_patterns(api_urlpatterns, allowed=['json'])

urlpatterns += api_urlpatterns

urlpatterns += patterns('',
    url(r'^app/login/$', 'myrg_webapp.views.login', name='login'),
    url(r'^app/logout/$', 'myrg_webapp.views.logout', name='logout'),
    url(r'^app/set_role_id/$', 'myrg_webapp.views.set_role_id'),
    url(r'^app/resource/(?P<resource_id>.+?)$', 'myrg_webapp.views.get_resource'),
    url(r'^$', WebApp.as_view(), name='home'),
)