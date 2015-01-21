from __future__ import unicode_literals
from future.builtins import *
import six

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from .models import PermissionDefinition, PermissionList

class PermissionAdmin(admin.ModelAdmin):
    list_display = (
                    'role_class',
                   )

    search_fields = ('role_class','definition')
    ordering = ('role_class',)
    
class PermissionListAdmin(admin.ModelAdmin):
    list_display = (
                    'permission', 'role_classes',
                   )

    search_fields = ('permission','role_classes')
    ordering = ('permission',)
    
    
    
    
admin.site.register(PermissionDefinition, PermissionAdmin)
admin.site.register(PermissionList, PermissionListAdmin)