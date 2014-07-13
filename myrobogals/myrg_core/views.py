from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.utils import timezone
import calendar

class Time(APIView):
    def metadata(self, request):
        """
        Don't include the view description in OPTIONS responses.
        """ 
        data = super(Now, self).metadata(request)
        data.pop('description')
        return data
    
    def get(self, request, format=None):
        time_now = timezone.now()
        return Response({
            "time": {
                "iso8601": time_now.isoformat(),
                "unix_ts": calendar.timegm(time_now.timetuple())
            }
        })

