from myrobogals.auth.models import User, Group
from myrobogals.rgteaching.models import School, SchoolVisit, TrainingSession, EventAttendee
from myrobogals import admin

class EventAttendeeAdmin(admin.TabularInline):
	model = EventAttendee
	extra = 10

class SchoolAdmin(admin.ModelAdmin):
	list_display = ('name', 'chapter', 'contact_person')
	search_fields = ('name', 'chapter', 'contact_person', 'contact_email', 'address')

class SchoolVisitAdmin(admin.ModelAdmin):
	list_display = ('school', 'chapter', 'visit_start')
	search_fields = ('school', 'chapter', 'visit_start')
	fieldsets = (
		(None, {'fields': ('school', 'chapter', 'creator', 'status', 'allow_rsvp')}),
		('Dates', {'fields': ('visit_start', 'visit_end')}),
		('Lesson info', {'fields': ('numstudents', 'yearlvl', 'numrobots', 'lessonnum', 'notes')}),
		('Preparation', {'fields': ('toprint', 'tobring', 'otherprep')}),
		('Information for volunteers', {'fields': ('location', 'meeting_location', 'meeting_time', 'contact', 'contact_email', 'contact_phone')}),
		('Closing comments', {'fields': ('closing_comments',)})
	)
	inlines = (EventAttendeeAdmin,)

class TrainingSessionAdmin(admin.ModelAdmin):
	list_display = ('chapter', 'visit_start', 'location')
	search_fields = ('location', 'chapter', 'visit_start')
	fieldsets = (
		(None, {'fields': ('location', 'chapter', 'creator', 'status', 'allow_rsvp')}),
		('Dates', {'fields': ('visit_start', 'visit_end')}),
		('Information for attendees', {'fields': ('meeting_location', 'meeting_time', 'contact', 'contact_email', 'contact_phone', 'notes')}),
	)
	inlines = (EventAttendeeAdmin,)

admin.site.register(School, SchoolAdmin)
admin.site.register(SchoolVisit, SchoolVisitAdmin)
admin.site.register(TrainingSession, TrainingSessionAdmin)
