'''
from myrobogals.rgteaching.models import Event
from pytz import timezone

# This is to be used once only, to upgrade the production myRobogals past Django 1.4, which introduced native timezone support
def convert_times():
	for e in Event.objects.all():
		tz = timezone(e.chapter.timezone.description)
		start = tz.localize(e.visit_start.replace(tzinfo=None))
		end = tz.localize(e.visit_end.replace(tzinfo=None))
		e.visit_start = start
		e.visit_end = end
		if e.meeting_time != None:
			meeting_time = tz.localize(e.meeting_time.replace(tzinfo=None))
			e.meeting_time = meeting_time
		e.save()
'''
