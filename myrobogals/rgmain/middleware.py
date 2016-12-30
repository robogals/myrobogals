import pytz
from django.utils import timezone

class TimezoneMiddleware(object):
    def process_request(self, request):
        if request.user.id:
            timezone.activate(request.user.tz_obj())
        else:
            timezone.deactivate()
