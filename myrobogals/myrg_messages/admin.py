"""
    myRobogals
    myrg_messages/admin.py

    2014
    Robogals Software Team
"""

from django.contrib import admin

from .models import EmailDefinition, SMSDefinition, EmailMessage, SMSMessage

class EmailDefinitionAdmin(admin.ModelAdmin):
    list_display = (
                    'sender_name',
                    'sender_address',
                    'subject',
                    'date_created',
                   )

    search_fields = ('sender_name','sender_address','subject',)
    ordering = ('-date_created',)
    
class EmailMessageAdmin(admin.ModelAdmin):
    list_display = (
                    'recipient_name',
                    'recipient_address',
                    'date_created',
                    'date_delivered',
                   )

    search_fields = ('recipient_name','recipient_address',)
    ordering = ('-date_created',)
    

admin.site.register(EmailDefinition, EmailDefinitionAdmin)
admin.site.register(EmailMessage, EmailMessageAdmin)