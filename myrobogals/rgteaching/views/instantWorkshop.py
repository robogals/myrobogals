import math
from django.http import Http404
from django.utils.timezone import make_aware

from myrobogals import settings
from django.contrib.auth.decorators import login_required
from myrobogals.rgteaching.forms import *
from myrobogals.rgteaching.models import (VISIT_TYPES_BASE, VISIT_TYPES_REPORT,
                                          DirectorySchool, Event,
                                          EventAttendee, EventMessage, School,
                                          SchoolVisit, SchoolVisitStats,
                                          StarSchoolDirectory)
from django.shortcuts import get_object_or_404, render_to_response
from django.template import Context, RequestContext, loader


"""
Creates and fills in the workshop with stats using 1 form
"""

@login_required
def instantvisit(request):

    # Obtain the user's chapter TODO: I dont like how this is set up
    if request.user.is_superuser and not settings.DEBUG: # TODO: Remove debug statement
        # Displays all schools directory for super user
        formchapter = None
    else:
        # Displays only the schools relavent to the chapter
        formchapter = request.user.chapter

    # Check if the user has exec rights
    if not request.user.is_staff and not request.user.is_superuser:
        raise Http404

    if request.method =='POST':
        if request.user.is_superuser:
            formpart1 = SchoolVisitFormInstant(request.POST, chapter = None)
            formpart2 = SchoolVisitStatsFormInstant(request.POST, chapter = None)
        else:
            formpart1 = SchoolVisitFormInstant(request.POST, chapter = formchapter)
            formpart2 = SchoolVisitStatsFormInstant(request.POST, chapter = formchapter)

        # Valid form
        if formpart1.is_valid() and formpart2.is_valid():
            data = formpart1.cleaned_data
            schoolVisit = formpart1.save(commit=False) # shit
            schoolVisit.chapter = chapter
            schoolVisit.creator = request.user
            schoolVisit.visit_start = make_aware(datetime.datetime.combine(data['date'], data['start_time']), timezone=chapter.tz_obj())
            schoolVisit.visit_end = make_aware(datetime.datetime.combine(data['date'], data['end_time']), timezone=chapter.tz_obj())
            schoolVisit.save()
            
            # Save attendance in database
            for attendee in data['attended']:
                list = EventAttendee.objects.filter(event__id=v.id).values_list('user_id', flat=True)
                if attendee.id not in list:
                    newinvite = EventAttendee()
                    newinvite.event = v
                    newinvite.user = attendee
                    newinvite.actual_status = 1
                    newinvite.rsvp_status = 0
                    newinvite.save()
            for person in EventAttendee.objects.filter(event__id=v.id):
                if person.user in data['attended']:
                    person.actual_status = 1
                    person.save()
                else:
                    person.actual_status = 2
                    person.save()
            
            # Render page 2: enter user-specific volunteering hours
            defaultHours = int(math.ceil((v.visit_end - v.visit_start).total_seconds() / 3600.0))

            request.session['hoursPerPersonStageInstant'] = 2

            return render_to_response('visit_hoursPerPerson.html', {'attended': data['attended'], 'visit_id': 0, 'defaultHours': range(defaultHours)}, context_instance=RequestContext(request))

        # Form is invalid
        else:
            return render_to_response('instant_workshop.html', {'form1': formpart1, 'form2': formpart2}, context_instance=RequestContext(request))
    # Not supposed to happen
    elif request.method == 'POST' and request.session['hoursPerPersonStage'] == 2:
        raise Http404        
    else:
        # Prepare form
        formpart1 = SchoolVisitFormInstant(chapter=formchapter)
        formpart2 = SchoolVisitStatsFormInstant(chapter=formchapter)

        # Render clean form
        return render_to_response('instant_workshop.html', {'form1': formpart1, 'form2': formpart2}, context_instance=RequestContext(request))