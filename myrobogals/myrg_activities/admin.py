from __future__ import unicode_literals
from future.builtins import *
import six


from django.contrib import admin

from .models import Activity, SubActivity, Participant, PecuniaryTransaction, ActivityItem, SubActivityItem

class ActivityAdmin(admin.ModelAdmin):
    list_display = (
                    'name',
                    'date_activity_start',
                    'date_activity_end',
                    'date_rsvp_open',
                    'date_rsvp_close',
                    'status',
                   )

    search_fields = ('name','description',)
    ordering = ('-date_rsvp_close','name',)
    
class SubActivityAdmin(admin.ModelAdmin):
    list_display = (
                    'parent',
                    'name',
                    'date_activity_start',
                    'date_activity_end',
                    'date_rsvp_open',
                    'date_rsvp_close',
                    )

    search_fields = ('name','description',)
    ordering = ('-date_rsvp_close','parent',)

class ParticipantAdmin(admin.ModelAdmin):
    list_display = (
                    'activity',
                    'participant_user',
                    'participant_role_class',
                    'participant_group',
                    'status',
                    'last_changed',
                   )

    search_fields = ('activity','participant_user','participant_role_class','participant_group',)
    ordering = ('-last_changed','activity',)

    def participant_user(self, instance):
        return instance.user_role.user

    def participant_role_class(self, instance):
        return instance.user_role.role_class

    def participant_group(self, instance):
        return instance.user_role.group
    
class PecuniaryTransactionAdmin(admin.ModelAdmin):
    list_display = (
                    'date',
                    'initiator_role',
                    'participant_role',
                    'label',
                    'amount',
                   )

    search_fields = ()
    ordering = ('-date',)

    def participant_role(self, instance):
        return instance.participant.user_role

class ActivityItemAdmin(admin.ModelAdmin):
    list_display = (
                    'name',
                    'order',
                    'date_open',
                    'date_close',
                   )

    search_fields = ('name','definition',)
    ordering = ('name','order')
    
class SubActivityItemAdmin(admin.ModelAdmin):
    list_display = (
                    'name',
                    'order',
                    'date_open',
                    'date_close',
                   )

    search_fields = ('name','definition',)
    ordering = ('name','order')



admin.site.register(Activity, ActivityAdmin)
admin.site.register(SubActivity, SubActivityAdmin)

admin.site.register(ActivityItem, ActivityItemAdmin)
admin.site.register(SubActivityItem, SubActivityItemAdmin)

admin.site.register(Participant, ParticipantAdmin)

admin.site.register(PecuniaryTransaction, PecuniaryTransactionAdmin)

