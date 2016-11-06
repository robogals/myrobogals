from myrobogals.rgconf.models import Conference, ConferencePart, ConferenceAttendee, ConferencePayment, ConferenceCurrency
from django.contrib import admin

class ConferenceAdmin(admin.ModelAdmin):
	list_display = ('name', 'start_date', 'end_date')

class ConferencePartAdmin(admin.ModelAdmin):
	list_display = ('conference', 'title', 'cost_formatted')
	list_filter = ('conference',)

class ConferenceAttendeeAdmin(admin.ModelAdmin):
	list_display = ('conference', 'first_name', 'last_name', 'chapter', 'mobile', 'total_cost_formatted', 'balance_owing_formatted')
	list_filter = ('conference',)

class ConferencePaymentAdmin(admin.ModelAdmin):
	list_display = ('date', 'attendee_name', 'conference', 'amount_formatted', 'payment_method')

admin.site.register(Conference, ConferenceAdmin)
admin.site.register(ConferencePart, ConferencePartAdmin)
admin.site.register(ConferenceAttendee, ConferenceAttendeeAdmin)
admin.site.register(ConferencePayment, ConferencePaymentAdmin)
admin.site.register(ConferenceCurrency)
