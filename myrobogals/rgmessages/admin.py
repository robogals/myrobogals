from myrobogals.rgmessages.models import EmailMessage, EmailRecipient, NewsletterSubscriber, Newsletter, SubscriberType
from myrobogals import admin

class EmailRecipientAdmin(admin.TabularInline):
	model = EmailRecipient
	extra = 2

class EmailMessageAdmin(admin.ModelAdmin):
	fieldsets = (
		('Headers', {'fields': ('from_address', 'from_name', 'subject', 'reply_address', 'html')}),
		('Message Body', {'fields': ('body',)}),
		('Other', {'fields': ('sender', 'status', 'date')})
	)
	
	list_display = ('subject', 'from_name', 'from_address', 'reply_address', 'date', 'status')
	search_fields = ('subject', 'from_name', 'from_address', 'reply_address')
	inlines = (EmailRecipientAdmin,)
	ordering = ('-date',)

class NewsletterSubscriberAdmin(admin.TabularInline):
	model = NewsletterSubscriber
	extra = 10

class SubscriberTypeAdmin(admin.ModelAdmin):
	list_display = ('description', 'order', 'public')

class NewsletterAdmin(admin.ModelAdmin):
	inlines = (NewsletterSubscriberAdmin,)

admin.site.register(SubscriberType, SubscriberTypeAdmin)
admin.site.register(Newsletter, NewsletterAdmin)
admin.site.register(EmailMessage, EmailMessageAdmin)
