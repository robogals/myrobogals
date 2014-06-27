"""
    myRobogals
    myrg_groups/admin.py

    2014
    Robogals Software Team
"""

from django.contrib import admin

from .models import Group, Chapter, School, Company, RoleType, Role

from .forms import RoleCreationForm, RoleChangeForm

class GroupAdmin(admin.ModelAdmin):
    list_display = (
                    'name',
                    'status',
                   )

    search_fields = ('name',)
    ordering = ('name',)
    
class RoleTypeAdmin(admin.ModelAdmin):
    list_display = (
                    'name',
                    'description',
                   )

    search_fields = ('name',)
    ordering = ('name',)

# Based upon django.contrib.auth.admin.UserAdmin

class RoleAdmin(admin.ModelAdmin):
    form = RoleChangeForm
    add_form = RoleCreationForm

    list_display = (
                    'user',
                    'role_type',
                    'group',
                   )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                        'user',
                        'role_type',
                        'group',
                        'date_start',
                        'date_end',
                      )
               }
        ),
    )

    search_fields = ('user__username','role_type__name',)
    ordering = ('user__username',)

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return super(RoleAdmin, self).get_fieldsets(request, obj)


    def get_form(self, request, obj=None, **kwargs):
        defaults = {}
        if obj is None:
            defaults.update({
                'form': self.add_form,
                'fields': admin.util.flatten_fieldsets(self.add_fieldsets),
            })
        defaults.update(kwargs)
        return super(RoleAdmin, self).get_form(request, obj, **defaults)


admin.site.register(Group, GroupAdmin)
admin.site.register(Chapter, GroupAdmin)
admin.site.register(School, GroupAdmin)
admin.site.register(Company, GroupAdmin)

admin.site.register(RoleType, RoleTypeAdmin)
admin.site.register(Role, RoleAdmin)
