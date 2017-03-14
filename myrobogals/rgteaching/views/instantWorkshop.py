import math

from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.timezone import make_aware

from myrobogals.rgteaching.forms import *
from myrobogals.rgteaching.models import EventAttendee, SchoolVisit, SchoolVisitStats

"""
Creates and fills in the workshop with stats using 1 form
"""


@login_required
def instantvisit(request):
    chapter = request.user.chapter

    # Check if the user has exec rights
    if not request.user.is_staff and not request.user.is_superuser:
        raise Http404

    if request.method == 'POST' and not request.session.get('hoursPerPersonStage', False):
        if request.user.is_superuser:
            formpart1 = SchoolVisitFormInstant(request.POST, chapter=None)
            formpart2 = SchoolVisitStatsFormInstant(request.POST, chapter=None)
        else:
            formpart1 = SchoolVisitFormInstant(request.POST, chapter=chapter)
            formpart2 = SchoolVisitStatsFormInstant(request.POST, chapter=chapter)

        # Valid form
        if formpart1.is_valid() and formpart2.is_valid():
            data = formpart1.cleaned_data
            data_stats = formpart2.cleaned_data

            schoolvisit = SchoolVisit()

            schoolvisit.chapter = chapter
            schoolvisit.creator = request.user
            schoolvisit.school = data['school']
            schoolvisit.location = data['location']
            schoolvisit.visit_start = make_aware(datetime.datetime.combine(data['date'], data['start_time']),
                                                 timezone=chapter.tz_obj())
            schoolvisit.visit_end = make_aware(datetime.datetime.combine(data['date'], data['end_time']),
                                               timezone=chapter.tz_obj())
            schoolvisit.save()

            # Add the new stats just entered
            stats = SchoolVisitStats()
            stats.visit = schoolvisit
            stats.visit_type = data_stats['visit_type']
            stats.primary_girls_first = data_stats['primary_girls_first']
            stats.primary_girls_repeat = data_stats['primary_girls_repeat']
            stats.primary_boys_first = data_stats['primary_boys_first']
            stats.primary_boys_repeat = data_stats['primary_boys_repeat']
            stats.high_girls_first = data_stats['high_girls_first']
            stats.high_girls_repeat = data_stats['high_girls_repeat']
            stats.high_boys_first = data_stats['high_boys_first']
            stats.high_boys_repeat = data_stats['high_boys_repeat']
            stats.other_girls_first = data_stats['other_girls_first']
            stats.other_girls_repeat = data_stats['other_girls_repeat']
            stats.other_boys_first = data_stats['other_boys_first']
            stats.other_boys_repeat = data_stats['other_boys_repeat']
            stats.notes = data_stats['notes']
            stats.save()

            # Save attendance in database
            for attendee in data_stats['attended']:
                newinvite = EventAttendee()
                newinvite.event = schoolvisit
                newinvite.user = attendee
                newinvite.actual_status = 1
                newinvite.rsvp_status = 0
                newinvite.save()

            # Render page 2: enter user-specific volunteering hours
            default_hours = int(math.ceil((schoolvisit.visit_end - schoolvisit.visit_start).total_seconds() / 3600.0))

            request.session['hoursPerPersonStage'] = 2

            return render_to_response('visit_hoursPerPerson.html', {'attended': data_stats['attended'], 'visit_id': schoolvisit.id,
                                                                    'defaultHours': range(default_hours)},
                                      context_instance=RequestContext(request))

        # Form is invalid
        else:
            return render_to_response('instant_workshop.html', {'form1': formpart1, 'form2': formpart2},
                                      context_instance=RequestContext(request))
    # Happens when someone presses back
    elif request.method == 'POST' and request.session['hoursPerPersonStage'] == 2:
        raise Http404
    else:
        # Prepare form
        if request.user.is_superuser:
            formpart1 = SchoolVisitFormInstant(chapter=None)
            formpart2 = SchoolVisitStatsFormInstant(chapter=None)
        else:
            formpart1 = SchoolVisitFormInstant(chapter=chapter)
            formpart2 = SchoolVisitStatsFormInstant(chapter=chapter)

        # Render clean form
        return render_to_response('instant_workshop.html', {'form1': formpart1, 'form2': formpart2},
                                  context_instance=RequestContext(request))
