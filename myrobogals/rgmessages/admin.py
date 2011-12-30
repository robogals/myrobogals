from myrobogals.rgmessages.models import SMSMessage, SMSRecipient, EmailMessage, EmailRecipient, NewsletterSubscriber, PendingNewsletterSubscriber, Newsletter, SubscriberType
from myrobogals import admin

class EmailRecipientAdmin(admin.TabularInline):
	model = EmailRecipient
	extra = 2

class EmailMessageAdmin(admin.ModelAdmin):
	fieldsets = (
		('Headers', {'fields': ('from_address', 'from_name', 'subject', 'reply_address', 'html')}),
		('Scheduling', {'fields': ('scheduled', 'scheduled_date', 'scheduled_date_type')}),
		('Message Body', {'fields': ('body',)}),
		('Other', {'fields': ('sender', 'status', 'date')})
	)
	
	list_display = ('subject', 'from_name', 'from_address', 'reply_address', 'date', 'status')
	search_fields = ('subject', 'from_name', 'from_address', 'reply_address')
	inlines = (EmailRecipientAdmin,)
	ordering = ('-date',)

class SMSRecipientAdmin(admin.TabularInline):
	model = SMSRecipient
	extra = 2

class SMSMessageAdmin(admin.ModelAdmin):
	fieldsets = (
		('Headers', {'fields': ('senderid', 'unicode', 'split',)}),
		('Scheduling', {'fields': ('scheduled', 'scheduled_date', 'scheduled_date_type')}),
		('Message Body', {'fields': ('body',)}),
		('Other', {'fields': ('sender', 'chapter', 'status', 'date')})
	)
	
	list_display = ('body', 'sender', 'date', 'credits_used', 'status')
	search_fields = ('body',)
	inlines = (SMSRecipientAdmin,)
	ordering = ('-date',)

class NewsletterSubscriberAdmin(admin.ModelAdmin):
	list_display = ('email', 'newsletter', 'first_name', 'last_name', 'company', 'country')
	search_fields = ('email', 'first_name', 'last_name', 'company')
	list_filter = ('newsletter',)

class SubscriberTypeAdmin(admin.ModelAdmin):
	list_display = ('description', 'order', 'public')

class NewsletterAdmin(admin.ModelAdmin):
	fieldsets = (
		(None, {'fields': ('name', 'from_name', 'from_email', 'from_user')}),
		('Confirmation email', {'fields': ('confirm_email', 'confirm_subject', 'confirm_url', 'confirm_from_name', 'confirm_from_email', 'confirm_from_user', 'confirm_html')})
	)

admin.site.register(SubscriberType, SubscriberTypeAdmin)
admin.site.register(NewsletterSubscriber, NewsletterSubscriberAdmin)
admin.site.register(Newsletter, NewsletterAdmin)
admin.site.register(EmailMessage, EmailMessageAdmin)
admin.site.register(SMSMessage, SMSMessageAdmin)
admin.site.register(PendingNewsletterSubscriber)
