"""
    myRobogals
    myrg_core/admin.py

    2014
    Robogals Software Team
"""

from django.contrib import admin

from .models import APILog

class APILogAdmin(admin.ModelAdmin):
    list_display = (
                    'get_user_from_role',
                    'get_group_from_role',
                    'get_role_class_from_role',
                    'ip',
                    'api_url',
                    'date',
                   )

    search_fields = (
                    'get_user_from_role',
                    'get_group_from_role',
                    'get_role_class_from_role',
                    'ip',
                    'api_url',
                    'date',
                    )
                    
    ordering = ('-date',)

    def get_user_from_role(self, obj):
        if obj.user_role is None:
            return None
        return obj.user_role.user
    get_user_from_role.short_description = 'User' 
    
    def get_group_from_role(self, obj):
        if obj.user_role is None:
            return None
        return obj.user_role.group
    get_group_from_role.short_description = 'Group' 
    
    def get_role_class_from_role(self, obj):
        if obj.user_role is None:
            return None
        return obj.user_role.role_class
    get_role_class_from_role.short_description = 'Role Class' 
    
admin.site.register(APILog, APILogAdmin)