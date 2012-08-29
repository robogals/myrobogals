from myrobogals.auth.models import User, Group
from myrobogals.rgteaching.models import School, DirectorySchool, SchoolVisit, SchoolVisitStats, TrainingSession, EventAttendee
from myrobogals import admin

class EventAttendeeAdmin(admin.TabularInline):
	model = EventAttendee
	extra = 10

class SchoolAdmin(admin.ModelAdmin):
	list_display = ('name', 'chapter', 'contact_person', 'address_state', 'address_country')
	search_fields = ('name', 'chapter', 'contact_person', 'contact_email', 'address')

class DirectorySchoolAdmin(admin.ModelAdmin):
	list_display = ('name', 'address_city', 'state_code', 'address_postcode', 'type', 'level', 'gender')
	search_fields = ('name', 'address_city', 'address_postcode')
	list_filter = ('type', 'level', 'gender', 'address_state')

class SchoolVisitAdmin(admin.ModelAdmin):
	list_display = ('school', 'chapter', 'visit_start')
	fieldsets = (
		(None, {'fields': ('school', 'chapter', 'creator', 'status', 'allow_rsvp')}),
		('Dates', {'fields': ('visit_start', 'visit_end')}),
		('Lesson info', {'fields': ('numstudents', 'yearlvl', 'numrobots', 'lessonnum', 'notes')}),
		('Preparation', {'fields': ('toprint', 'tobring', 'otherprep')}),
		('Information for volunteers', {'fields': ('location', 'meeting_location', 'meeting_time', 'contact', 'contact_email', 'contact_phone')}),
		('Closing comments', {'fields': ('closing_comments',)})
	)
	list_filter = ('chapter',)
	inlines = (EventAttendeeAdmin,)

'''
class TrainingSessionAdmin(admin.ModelAdmin):
	list_display = ('chapter', 'visit_start', 'location')
	search_fields = ('location', 'chapter', 'visit_start')
	fieldsets = (
		(None, {'fields': ('location', 'chapter', 'creator', 'status', 'allow_rsvp')}),
		('Dates', {'fields': ('visit_start', 'visit_end')}),
		('Information for attendees', {'fields': ('meeting_location', 'meeting_time', 'contact', 'contact_email', 'contact_phone', 'notes')}),
	)
	inlines = (EventAttendeeAdmin,)
'''

class SchoolVisitStatsAdmin(admin.ModelAdmin):
	list_display = ('visit', 'chapter', 'num_girls')

admin.site.register(School, SchoolAdmin)
admin.site.register(DirectorySchool, DirectorySchoolAdmin)
admin.site.register(SchoolVisit, SchoolVisitAdmin)
admin.site.register(SchoolVisitStats, SchoolVisitStatsAdmin)
#admin.site.register(TrainingSession, TrainingSessionAdmin)
