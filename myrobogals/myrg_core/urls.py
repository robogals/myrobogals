from __future__ import unicode_literals
from future.builtins import *
import six

from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import Group
from myrg_users.models import RobogalsUser

from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns

from myrg_core.views import Time
from myrg_users.views import ListUsers, DeleteUsers, EditUsers, CreateUsers, ResetUserPasswords, ResetUserPasswordsComplete, WhoAmI, ListMyRoles, KillSessions
from myrg_groups.views import ListGroups, DeleteGroups, EditGroups, CreateGroups, ListRoles, EditRoles, CreateRoles, ListRoleClasses, DeleteRoleClasses, EditRoleClasses, CreateRoleClasses
from myrg_messages.views import SendMessage, ListEmailDefinition, ListEmailMessage
from myrg_repo.views import ListRepoFiles, DeleteRepoFiles, ListRepoContainers, DeleteRepoContainers, EditRepoContainers, CreateRepoContainers
from myrg_permissions.views import ListPermission, DeletePermissionLists, EditPermissionLists, CreatePermissionLists

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
    url(r'^api/1.0/utils/pwdreset/complete', ResetUserPasswordsComplete.as_view()),

    url(r'^api/1.0/self/whoami$', WhoAmI.as_view()),
    url(r'^api/1.0/self/roles$', ListMyRoles.as_view()),
    url(r'^api/1.0/self/killsessions$', KillSessions.as_view()),

    url(r'^api/1.0/users/list$', ListUsers.as_view()),
    url(r'^api/1.0/users/delete$', DeleteUsers.as_view()),
    url(r'^api/1.0/users/edit$', EditUsers.as_view()),
    url(r'^api/1.0/users/create$', CreateUsers.as_view()),

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
    
    url(r'^api/1.0/emailmessage/list$', ListEmailMessage.as_view()),
    url(r'^api/1.0/emaildefinitions/list$', ListEmailDefinition.as_view()),
    url(r'^api/1.0/repofiles/list$', ListRepoFiles.as_view()),
    url(r'^api/1.0/repofiles/delete$', DeleteRepoFiles.as_view()),
    url(r'^api/1.0/repofiles/create', 'myrg_repo.views.upload', name='upload'),

    url(r'^api/1.0/repocontainers/list$', ListRepoContainers.as_view()),
    url(r'^api/1.0/repocontainers/delete$', DeleteRepoContainers.as_view()),
    url(r'^api/1.0/repocontainers/edit$', EditRepoContainers.as_view()),
    url(r'^api/1.0/repocontainers/create$', CreateRepoContainers.as_view()),
    
    url(r'^api/1.0/permissions/list$', ListPermission.as_view()),
    url(r'^api/1.0/permissions/delete$', DeletePermissionLists.as_view()),
    url(r'^api/1.0/permissions/edit$', EditPermissionLists.as_view()),
    url(r'^api/1.0/permissions/create$', CreatePermissionLists.as_view()),

    url(r'^api/1.0/messages/send$', SendMessage.as_view()),
)

api_urlpatterns = format_suffix_patterns(api_urlpatterns, allowed=['json'])

urlpatterns += api_urlpatterns

urlpatterns += patterns('',
    url(r'^app/login$', 'myrg_webapp.views.login', name='login'),
    url(r'^app/logout$', 'myrg_webapp.views.logout', name='logout'),
    url(r'^app/set_role_id$', 'myrg_webapp.views.set_role_id'),
    url(r'^app/resource/(?P<resource_id>.+?)$', 'myrg_webapp.views.get_resource'),
    
    url(r'^$', 'myrg_webapp.views.webapp', name='home'),
    url(r'^app/url/csv', 'myrg_reports.csv.convert_csv_direct', name='csv_direct'),
    url(r'^app/csv', 'myrg_reports.csv.convert_csv', name='csv'),
    #url(r'^app/report', 'myrg_reports.views.my_report', name='report')
    #url(r'^/(?P<app_label>[\d\w]+)/(?P<model_name>[\d\w]+)/csv/', 'myrg_repo.views.convert_csv')
)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
