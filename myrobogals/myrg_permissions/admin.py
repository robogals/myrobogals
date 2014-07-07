"""
    myRobogals
    myrg_permissions/admin.py

    2014
    Robogals Software Team
"""

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