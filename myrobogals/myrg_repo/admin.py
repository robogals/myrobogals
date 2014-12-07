from __future__ import unicode_literals
from future.builtins import *
import six


from django.contrib import admin

from .models import RepoContainer, RepoFile

#from .forms import RoleCreationForm, RoleChangeForm
    
    
class RepoContainerAdmin(admin.ModelAdmin):
    list_display = (
                    'title',
                    'body',
                    'tags',
                   )

    search_fields = ('title',)
    ordering = ('title',)

# Based upon django.contrib.auth.admin.UserAdmin

class RepoFileAdmin(admin.ModelAdmin):
    #form = RoleChangeForm
    #add_form = RoleCreationForm

    list_display = (
                    'container',
                    'name',
                    'file',
                   )


    search_fields = ('name',)
    ordering = ('name',)

#    def get_fieldsets(self, request, obj=None):
#        if not obj:
#            return self.add_fieldsets
#        return super(RoleAdmin, self).get_fieldsets(request, obj)


#    def get_form(self, request, obj=None, **kwargs):
#        defaults = {}
#        if obj is None:
#            defaults.update({
#                'form': self.add_form,
#                'fields': admin.utils.flatten_fieldsets(self.add_fieldsets),
#            })
#        defaults.update(kwargs)
#        return super(RoleAdmin, self).get_form(request, obj, **defaults)



admin.site.register(RepoContainer, RepoContainerAdmin)
admin.site.register(RepoFile, RepoFileAdmin)
