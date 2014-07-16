from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.models import Group
from myrg_users.models import RobogalsUser

from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns

from myrg_core.views import Time
from myrg_users.views import ListUsers, DeleteUsers, EditUsers, CreateUsers, ResetUserPasswords, WhoAmI, KillSessions
from myrg_groups.views import ListGroups, DeleteGroups, EditGroups, CreateGroups, ListRoles, EditRoles, CreateRoles, ListRoleClasses, DeleteRoleClasses, EditRoleClasses, CreateRoleClasses 
from myrg_messages.views import SendMessage



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
    #url(r'^api/1.0/utils/pwdreset/complete', ResetUserPasswordsComplete.as_view()),
    
    url(r'^api/1.0/users/list$', ListUsers.as_view()),
    url(r'^api/1.0/users/delete$', DeleteUsers.as_view()),
    url(r'^api/1.0/users/edit$', EditUsers.as_view()),
    url(r'^api/1.0/users/create$', CreateUsers.as_view()),
    
    url(r'^api/1.0/self/whoami$', WhoAmI.as_view()),
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
    
    url(r'^api/1.0/messages/send$', SendMessage.as_view()),
)

    
api_urlpatterns = format_suffix_patterns(api_urlpatterns, allowed=['json'])

urlpatterns += api_urlpatterns

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
