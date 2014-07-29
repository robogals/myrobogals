from __future__ import unicode_literals
from future.builtins import *
import six

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from .models import PermissionDefinition

class PermissionAdmin(admin.ModelAdmin):
    list_display = (
                    'role_class',
                   )

    search_fields = ('role_class','definition')
    ordering = ('role_class',)
    
    
    
    
admin.site.register(PermissionDefinition, PermissionAdmin)