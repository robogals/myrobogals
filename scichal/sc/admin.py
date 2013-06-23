from django.contrib import admin
from scichal.sc.models import Entrant, EmailMessage, MinorChallenge, MinorChallengeEntry

class EntrantAdmin(admin.ModelAdmin):
    search_fields = ('name', 'mentor_name', 'email', 'mentor_phone', 'school', 'username')
    list_display = ('name', 'age', 'mentor_name', 'mentor_phone', 'email', 'school', 'comment', 'date_registered', 'submitted')

admin.site.register(Entrant, EntrantAdmin)
admin.site.register(EmailMessage)
admin.site.register(MinorChallenge)
admin.site.register(MinorChallengeEntry)