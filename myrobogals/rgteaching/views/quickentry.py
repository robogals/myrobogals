"""
Creates and fills in the workshop with stats using a single form
"""

import math

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.utils.timezone import make_aware

from myrobogals.rgteaching.forms import *
from myrobogals.rgteaching.models import EventAttendee, SchoolVisit, SchoolVisitStats


@login_required
def instantvisit(request):
    chapter = request.user.chapter

    # Check if the user has exec rights
    if not request.user.is_staff and not request.user.is_superuser:
        raise Http404

    if not request.session.get('hoursPerPersonStage', False):
        request.session['hoursPerPersonStage'] = 1

    # Sometimes request.session['hoursPerPersonStage'] may equal 1 from editing stats from a closed workshop
    if request.method == 'POST' and request.session['hoursPerPersonStage'] != 2:
        if request.user.is_superuser:
            formpart1 = SchoolVisitFormInstant(request.POST, chapter=None)
            formpart2 = SchoolVisitStatsFormInstant(request.POST, chapter=None)
        else:
            formpart1 = SchoolVisitFormInstant(request.POST, chapter=chapter)
            formpart2 = SchoolVisitStatsFormInstant(request.POST, chapter=chapter)

        form_school = SchoolFormPartOne(request.POST, chapter=chapter, school_id=0)

        # Validate form
        if formpart1.is_valid() and formpart2.is_valid():
            data = formpart1.cleaned_data
            data_stats = formpart2.cleaned_data

            selected_school = data['school']
            school_visit = SchoolVisit()
            new_school = School()

            school_visit.created_method = 1

            # Check if new school was selected, New school equals to 0
            if selected_school == u'0':
                if form_school.is_valid():
                    new_school_form = form_school.cleaned_data

                    # Check if school exists
                    exist = School.objects.filter(name__iexact=new_school_form['name'], chapter=chapter)
                    if exist:
                        messages.error(request, "School seems to already exist, please recheck list.")
                        return render_to_response('instant_workshop.html',
                                                  {'form1': formpart1, 'form2': formpart2, 'schoolform': form_school},
                                                  context_instance=RequestContext(request))

                    # Create new school after checking it doesn't exist
                    new_school.name = new_school_form['name']
                    new_school.chapter = chapter
                    new_school.address_street = new_school_form['address_street']
                    new_school.address_city = new_school_form['address_city']
                    new_school.address_state = new_school_form['address_state']
                    new_school.address_country = new_school_form['address_country']
                    new_school.save()
                    school_visit.school = new_school
                else:
                    # School form invalid
                    return render_to_response('instant_workshop.html',
                                              {'form1': formpart1, 'form2': formpart2, 'schoolform': form_school},
                                              context_instance=RequestContext(request))
            else:
                try:
                    previously_visited_school = School.objects.get(name=selected_school, chapter=chapter)
                except ObjectDoesNotExist:
                    messages.error(request,
                                   message=unicode("Please select a school from the list or create a new one."))
                    return render_to_response('instant_workshop.html',
                                              {'form1': formpart1, 'form2': formpart2, 'schoolform': form_school},
                                              context_instance=RequestContext(request))
                school_visit.school = previously_visited_school

            school_visit.chapter = chapter
            school_visit.creator = request.user
            school_visit.location = data['location']
            school_visit.visit_start = make_aware(datetime.datetime.combine(data['date'], data['start_time']),
                                                  timezone=chapter.tz_obj())
            school_visit.visit_end = make_aware(datetime.datetime.combine(data['date'], data['end_time']),
                                                timezone=chapter.tz_obj())
            school_visit.save()

            # Add the new stats just entered
            stats = SchoolVisitStats()
            stats.visit = school_visit
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
                newinvite.event = school_visit
                newinvite.user = attendee
                newinvite.actual_status = 1
                newinvite.rsvp_status = 0
                newinvite.save()

            # Render page 2: enter user-specific volunteering hours
            default_hours = int(math.ceil((school_visit.visit_end - school_visit.visit_start).total_seconds() / 3600.0))

            request.session['hoursPerPersonStage'] = 2

            return render_to_response('visit_hoursPerPerson.html',
                                      {'attended': data_stats['attended'], 'visit_id': school_visit.id,
                                       'defaultHours': range(default_hours)},
                                      context_instance=RequestContext(request))

        # Form is invalid
        else:
            return render_to_response('instant_workshop.html',
                                      {'form1': formpart1, 'form2': formpart2, 'schoolform': form_school},
                                      context_instance=RequestContext(request))

    # Happens when someone presses back - refer them to the workshop list page to refill stats there
    elif request.method == 'POST' and request.session['hoursPerPersonStage'] == 2:
        del request.session['hoursPerPersonStage']
        messages.info(request,
                      message='An error occurred, find your newly created workshop here and refill in your stats.')
        return redirect('/teaching/list/')

    # Prepare form
    if request.user.is_superuser:
        formpart1 = SchoolVisitFormInstant(chapter=None)
        formpart2 = SchoolVisitStatsFormInstant(chapter=None)
    else:
        formpart1 = SchoolVisitFormInstant(chapter=chapter)
        formpart2 = SchoolVisitStatsFormInstant(chapter=chapter)

    form_school = SchoolFormPartOne(chapter=chapter, school_id=0)

    # Render clean form
    return render_to_response('instant_workshop.html',
                              {'form1': formpart1, 'form2': formpart2, 'schoolform': form_school},
                              context_instance=RequestContext(request))
