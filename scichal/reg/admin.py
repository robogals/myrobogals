from django.contrib import admin
from reg.models import JosDonations

class JosDonationsAdmin(admin.ModelAdmin):
    search_fields = ('firstname', 'other', 'email', 'phone')
    list_display = ('firstname', 'organization', 'mentor', 'relationship', 'email', 'phone', 'school', 'date_registered', 'user', 'payment_status', 'submitted')
    fieldsets = (
        (None, {'fields': ('firstname', 'organization', 'other', 'email', 'phone')}),
    )

admin.site.register(JosDonations, JosDonationsAdmin)
