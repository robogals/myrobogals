from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.utils.timezone import make_aware

from myrobogals.rgteaching.forms import *
from myrobogals.rgteaching.models import (Event,
                                          SchoolVisit, SchoolVisitStats)

"""
View for global reporting
"""


# Display reporting at a chapter level
@login_required
def report_standard(request):
    # Redirect superusers to global reports
    if request.user.is_superuser:
        return HttpResponseRedirect('/globalreports/')
    else:
        # Redirect global and regional exec to global reports
        if not request.user.is_staff:
            raise Http404  # Don't allow ordinary users to see any reports
        else:
            if request.user.chapter.pk == 1:
                return HttpResponseRedirect('/globalreports/')
            elif request.user.chapter.parent:
                if request.user.chapter.parent.pk == 1:
                    return HttpResponseRedirect('/globalreports/')
                else:
                    pass
            else:
                pass

    # If we reached here, we must be a chapter exec
    if request.method == 'POST':
        theform = ReportSelectorForm(request.POST)
        if theform.is_valid():
            formdata = theform.cleaned_data

            # Interpret the dates as having been entered in the user's local time
            start_date = make_aware(datetime.datetime.combine(formdata['start_date'], datetime.time.min),
                                    timezone=request.user.tz_obj())
            end_date = make_aware(datetime.datetime.combine(formdata['end_date'], datetime.time.max),
                                  timezone=request.user.tz_obj())

            event_id_list = Event.objects.filter(visit_start__range=[start_date, end_date],
                                                 chapter=request.user.chapter, status=1).values_list('id', flat=True)
            stats_list = SchoolVisitStats.objects.filter(visit__id__in=event_id_list)
            event_list = SchoolVisit.objects.filter(event_ptr__in=event_id_list).values_list('school', flat=True)
            visit_ids = SchoolVisit.objects.filter(event_ptr__in=event_id_list).values_list('id')
            visited_schools = {}
            totals = {}
            attendance = {}
            attendance_filtered = {}
            volunteer_hours = 0
            totals['visits'] = 0
            totals['pgf'] = 0
            totals['pgr'] = 0
            totals['pbf'] = 0
            totals['pbr'] = 0
            totals['hgf'] = 0
            totals['hgr'] = 0
            totals['hbf'] = 0
            totals['hbr'] = 0
            totals['ogf'] = 0
            totals['ogr'] = 0
            totals['obf'] = 0
            totals['obr'] = 0
            event_list = set(event_list)

            # For each school that had an event (workshop) during the period
            for school_id in event_list:
                school = School.objects.get(id=school_id)
                visited_schools[school.name] = {}
                visited_schools[school.name]['name'] = school.name
                visited_schools[school.name]['visits'] = 0
                visited_schools[school.name]['pgf'] = 0
                visited_schools[school.name]['pgr'] = 0
                visited_schools[school.name]['pbf'] = 0
                visited_schools[school.name]['pbr'] = 0
                visited_schools[school.name]['hgf'] = 0
                visited_schools[school.name]['hgr'] = 0
                visited_schools[school.name]['hbf'] = 0
                visited_schools[school.name]['hbr'] = 0
                visited_schools[school.name]['ogf'] = 0
                visited_schools[school.name]['ogr'] = 0
                visited_schools[school.name]['obf'] = 0
                visited_schools[school.name]['obr'] = 0
                this_schools_visits = SchoolVisitStats.objects.filter(visit__school=school,
                                                                      visit__visit_start__range=[start_date, end_date],
                                                                      visit__status=1)
                if int(formdata['visit_type']) == -1:
                    # include all stats categories
                    pass
                elif int(formdata['visit_type']) == -2:
                    # include both metro and regional robotics workshops
                    this_schools_visits = this_schools_visits.filter(visit_type__in=[0, 7])
                else:
                    # only include specific stats category
                    this_schools_visits = this_schools_visits.filter(visit_type=formdata['visit_type'])

                # For each visit at this school during the period
                for each_visit in this_schools_visits:
                    # totals for this school
                    visited_schools[school.name]['pgf'] += xint(each_visit.primary_girls_first)
                    visited_schools[school.name]['pgr'] += xint(each_visit.primary_girls_repeat)
                    visited_schools[school.name]['pbf'] += xint(each_visit.primary_boys_first)
                    visited_schools[school.name]['pbr'] += xint(each_visit.primary_boys_repeat)
                    visited_schools[school.name]['hgf'] += xint(each_visit.high_girls_first)
                    visited_schools[school.name]['hgr'] += xint(each_visit.high_girls_repeat)
                    visited_schools[school.name]['hbf'] += xint(each_visit.high_boys_first)
                    visited_schools[school.name]['hbr'] += xint(each_visit.high_boys_repeat)
                    visited_schools[school.name]['ogf'] += xint(each_visit.other_girls_first)
                    visited_schools[school.name]['ogr'] += xint(each_visit.other_girls_repeat)
                    visited_schools[school.name]['obf'] += xint(each_visit.other_boys_first)
                    visited_schools[school.name]['obr'] += xint(each_visit.other_boys_repeat)
                    visited_schools[school.name]['visits'] += 1
                    # overall totals
                    totals['pgf'] += xint(each_visit.primary_girls_first)
                    totals['pgr'] += xint(each_visit.primary_girls_repeat)
                    totals['pbf'] += xint(each_visit.primary_boys_first)
                    totals['pbr'] += xint(each_visit.primary_boys_repeat)
                    totals['hgf'] += xint(each_visit.high_girls_first)
                    totals['hgr'] += xint(each_visit.high_girls_repeat)
                    totals['hbf'] += xint(each_visit.high_boys_first)
                    totals['hbr'] += xint(each_visit.high_boys_repeat)
                    totals['ogf'] += xint(each_visit.other_girls_first)
                    totals['ogr'] += xint(each_visit.other_girls_repeat)
                    totals['obf'] += xint(each_visit.other_boys_first)
                    totals['obr'] += xint(each_visit.other_boys_repeat)
                    totals['visits'] += 1
                visited_schools[school.name]['gf'] = visited_schools[school.name]['pgf'] + visited_schools[school.name][
                    'hgf'] + visited_schools[school.name]['ogf']
                visited_schools[school.name]['gr'] = visited_schools[school.name]['pgr'] + visited_schools[school.name][
                    'hgr'] + visited_schools[school.name]['ogr']
                visited_schools[school.name]['bf'] = visited_schools[school.name]['pbf'] + visited_schools[school.name][
                    'hbf'] + visited_schools[school.name]['obf']
                visited_schools[school.name]['br'] = visited_schools[school.name]['pbr'] + visited_schools[school.name][
                    'hbr'] + visited_schools[school.name]['obr']
                if visited_schools[school.name]['visits'] == 0:
                    del visited_schools[school.name]
                totals['gf'] = totals['pgf'] + totals['hgf'] + totals['ogf']
                totals['gr'] = totals['pgr'] + totals['hgr'] + totals['ogr']
                totals['bf'] = totals['pbf'] + totals['hbf'] + totals['obf']
                totals['br'] = totals['pbr'] + totals['hbr'] + totals['obr']
            # attendance reporting
            user_list = User.objects.filter(chapter=request.user.chapter)

            for volunteer in user_list:
                attendance[volunteer.get_full_name()] = [0, 0]
                for attended in EventAttendee.objects.filter(actual_status=1, event__id__in=visit_ids,
                                                             user__id=volunteer.id):
                    type_id = SchoolVisit.objects.get(pk=attended.event.pk).schoolvisitstats_set.all()[0].visit_type
                    if int(formdata['visit_type']) == -1:
                        # include all stats categories
                        attendance[volunteer.get_full_name()][0] += 1
                        volunteer_hours = attended.hours
                        attendance[volunteer.get_full_name()][1] += int(volunteer_hours)
                    elif int(formdata['visit_type']) == -2:
                        # include both metro and regional robotics workshops
                        if type_id == 0 or type_id == 7:
                            attendance[volunteer.get_full_name()][0] += 1
                            volunteer_hours = attended.hours
                            attendance[volunteer.get_full_name()][1] += int(volunteer_hours)
                    else:
                        if type_id == int(formdata['visit_type']):
                            attendance[volunteer.get_full_name()][0] += 1
                            volunteer_hours = attended.hours
                            attendance[volunteer.get_full_name()][1] += int(volunteer_hours)

            for name, num_visits in attendance.iteritems():
                if num_visits > 0:
                    attendance_filtered[name] = num_visits
            attendance_sorted = sorted(attendance_filtered.iteritems(), key=itemgetter(1), reverse=True)
        else:
            totals = {}
            visited_schools = {}
            attendance_sorted = {}
    else:
        theform = ReportSelectorForm()
        totals = {}
        visited_schools = {}
        attendance_sorted = {}
    return render_to_response('stats_get_report.html',
                              {'theform': theform, 'totals': totals, 'schools': sorted(visited_schools.iteritems()),
                               'attendance': attendance_sorted}, context_instance=RequestContext(request))


# Global workshop reports
@login_required
def report_global(request):
    # Allow superusers to see these reports
    if not request.user.is_superuser:
        # Allow global and regional exec to see these reports
        if not request.user.is_staff:
            raise Http404
        else:
            if request.user.chapter.pk == 1:
                pass
            elif request.user.chapter.parent:
                if request.user.chapter.parent.pk == 1:
                    pass
                else:
                    raise Http404
            else:
                raise Http404

    warning = ''
    printview = False
    if request.method == 'POST':
        theform = ReportSelectorForm(request.POST)
        if theform.is_valid():
            formdata = theform.cleaned_data
            printview = formdata['printview']
            chapter_totals = {}
            region_totals = {}
            global_totals = {}

            # Interpret the dates as having been entered in the user's local time
            start_date = make_aware(datetime.datetime.combine(formdata['start_date'], datetime.time.min),
                                    timezone=request.user.tz_obj())
            end_date = make_aware(datetime.datetime.combine(formdata['end_date'], datetime.time.max),
                                  timezone=request.user.tz_obj())

            request.session['globalReportStartDate'] = start_date
            request.session['globalReportEndDate'] = end_date
            request.session['globalReportVisitType'] = formdata['visit_type']
            if start_date.date() < datetime.date(2011, 2, 11):
                warning = 'Warning: Australian data prior to 10 September 2010 and UK data prior to 11 February 2011 may not be accurate'
            chapters = Chapter.objects.filter(exclude_in_reports=False)
            for chapter in chapters:
                chapter_totals[chapter.short_en] = {}
                chapter_totals[chapter.short_en]['workshops'] = 0
                chapter_totals[chapter.short_en]['schools'] = 0
                chapter_totals[chapter.short_en]['first'] = 0
                chapter_totals[chapter.short_en]['repeat'] = 0
                chapter_totals[chapter.short_en]['girl_workshops'] = 0
                chapter_totals[chapter.short_en]['weighted'] = 0
                event_id_list = Event.objects.filter(visit_start__range=[start_date, end_date], chapter=chapter,
                                                     status=1).values_list('id', flat=True)
                event_list = SchoolVisit.objects.filter(event_ptr__in=event_id_list).values_list('school', flat=True)
                visit_ids = SchoolVisit.objects.filter(event_ptr__in=event_id_list).values_list('id')
                event_list = set(event_list)

                # For each school that had an event during the period
                for school_id in event_list:
                    # Get all visits at this school during the period
                    this_schools_visits = SchoolVisitStats.objects.filter(visit__school__id=school_id,
                                                                          visit__visit_start__range=[start_date,
                                                                                                     end_date],
                                                                          visit__status=1)
                    if int(formdata['visit_type']) == -1:
                        # include all stats categories
                        pass
                    elif int(formdata['visit_type']) == -2:
                        # include both metro and regional robotics workshops
                        this_schools_visits = this_schools_visits.filter(visit_type__in=[0, 7])
                    else:
                        # only include specific stats category
                        this_schools_visits = this_schools_visits.filter(visit_type=formdata['visit_type'])
                    if this_schools_visits:
                        chapter_totals[chapter.short_en]['schools'] += 1
                        for each_visit in this_schools_visits:
                            chapter_totals[chapter.short_en]['first'] += xint(each_visit.primary_girls_first) + xint(
                                each_visit.high_girls_first) + xint(each_visit.other_girls_first)
                            chapter_totals[chapter.short_en]['repeat'] += xint(each_visit.primary_girls_repeat) + xint(
                                each_visit.high_girls_repeat) + xint(each_visit.other_girls_repeat)
                            chapter_totals[chapter.short_en]['workshops'] += 1
                chapter_totals[chapter.short_en]['girl_workshops'] += chapter_totals[chapter.short_en]['first'] + \
                                                                      chapter_totals[chapter.short_en]['repeat']
                chapter_totals[chapter.short_en]['weighted'] = chapter_totals[chapter.short_en]['first'] + (
                float(chapter_totals[chapter.short_en]['repeat']) / 2)

                # Regional and Global Totals
                if chapter.parent:
                    if chapter.parent.short_en not in region_totals:
                        region_totals[chapter.parent.short_en] = {}
                    for key, value in chapter_totals[chapter.short_en].iteritems():
                        if key in region_totals[chapter.parent.short_en]:
                            region_totals[chapter.parent.short_en][key] += value
                        else:
                            region_totals[chapter.parent.short_en][key] = value
                        if key in global_totals:
                            global_totals[key] += value
                        else:
                            global_totals[key] = value
                    if chapter.parent.id == 1:
                        del chapter_totals[chapter.short_en]
                    elif chapter_totals[chapter.short_en]['workshops'] == 0:
                        del chapter_totals[chapter.short_en]
                elif chapter.id == 1:
                    del chapter_totals[chapter.short_en]
            del region_totals['Global']
        else:
            totals = {}
            chapter_totals = {}
            region_totals = {}
            global_totals = {}
    else:
        theform = ReportSelectorForm()
        chapter_totals = {}
        region_totals = {}
        global_totals = {}
    if request.user.is_superuser or request.user.chapter.id == 1:
        user_chapter_children = Chapter.objects.filter(exclude_in_reports=False).values_list('short_en', flat=True)
    else:
        user_chapter_children = Chapter.objects.filter(parent__pk=request.user.chapter.pk,
                                                       exclude_in_reports=False).values_list('short_en', flat=True)
    if printview:
        return render_to_response('print_report.html', {'chapter_totals': sorted(chapter_totals.iteritems()),
                                                        'region_totals': sorted(region_totals.iteritems()),
                                                        'global': global_totals, 'warning': warning},
                                  context_instance=RequestContext(request))
    else:
        return render_to_response('stats_get_global_report.html',
                                  {'theform': theform, 'chapter_totals': sorted(chapter_totals.iteritems()),
                                   'region_totals': sorted(region_totals.iteritems()), 'global': global_totals,
                                   'warning': warning, 'user_chapter_children': set(user_chapter_children)},
                                  context_instance=RequestContext(request))


# This view is for when a chapter is clicked on in the global reports to see
# chapter-specific stats
# TODO: the URL should use myrobogals_url, not short_en
@login_required
def report_global_breakdown(request, chaptershorten):
    chapter = get_object_or_404(Chapter, short_en=chaptershorten)
    if (not request.user.is_staff) and (not request.user.is_superuser):
        raise Http404
    if (not chapter.parent) or (not chapter.parent.parent):
        raise Http404
    if (not request.user.is_superuser) and (request.user.chapter.pk != chapter.parent.pk) and (
        request.user.chapter.pk != chapter.parent.parent.pk):
        raise Http404
    if (not request.session.get('globalReportStartDate', False)) or (
    not request.session.get('globalReportEndDate', False)) or (not request.session.get('globalReportVisitType', False)):
        raise Http404
    start_date = request.session.get('globalReportStartDate', False)
    end_date = request.session.get('globalReportEndDate', False)
    visit_type = request.session.get('globalReportVisitType', False)
    chapter_totals = {}
    attendance = {}
    for u in User.objects.filter(chapter=chapter):
        attendance[u.get_full_name()] = {}
        attendance[u.get_full_name()]['workshops'] = 0
        attendance[u.get_full_name()]['schools'] = 0
        attendance[u.get_full_name()]['first'] = 0
        attendance[u.get_full_name()]['repeat'] = 0
        attendance[u.get_full_name()]['girl_workshops'] = 0
        attendance[u.get_full_name()]['weighted'] = 0
    chapter_totals[chapter.short_en] = {}
    chapter_totals[chapter.short_en]['workshops'] = 0
    chapter_totals[chapter.short_en]['schools'] = 0
    chapter_totals[chapter.short_en]['first'] = 0
    chapter_totals[chapter.short_en]['repeat'] = 0
    chapter_totals[chapter.short_en]['girl_workshops'] = 0
    chapter_totals[chapter.short_en]['weighted'] = 0
    event_id_list = Event.objects.filter(visit_start__range=[start_date, end_date], chapter=chapter,
                                         status=1).values_list('id', flat=True)
    event_list = SchoolVisit.objects.filter(event_ptr__in=event_id_list).values_list('school', flat=True)
    visit_ids = SchoolVisit.objects.filter(event_ptr__in=event_id_list).values_list('id')
    event_list = set(event_list)
    for school_id in event_list:
        this_schools_visits = SchoolVisitStats.objects.filter(visit__school__id=school_id,
                                                              visit__visit_start__range=[start_date, end_date],
                                                              visit__status=1)
        if int(visit_type) == -1:
            # include all stats categories
            pass
        elif int(visit_type) == -2:
            # include both metro and regional robotics workshops
            this_schools_visits = this_schools_visits.filter(visit_type__in=[0, 7])
        else:
            # only include specific stats category
            this_schools_visits = this_schools_visits.filter(visit_type=visit_type)
        if this_schools_visits:
            chapter_totals[chapter.short_en]['schools'] += 1
            for eventattendee in User.objects.filter(pk__in=EventAttendee.objects.filter(
                    event__pk__in=this_schools_visits.values_list('visit__event_ptr_id', flat=True)).values_list(
                    'user_id', flat=True)):
                try:
                    attendance[eventattendee.get_full_name()]['schools'] += 1
                except:
                    pass
            for each_visit in this_schools_visits:
                first = xint(each_visit.primary_girls_first) + xint(each_visit.high_girls_first) + xint(
                    each_visit.other_girls_first)
                chapter_totals[chapter.short_en]['first'] += first
                repeat = xint(each_visit.primary_girls_repeat) + xint(each_visit.high_girls_repeat) + xint(
                    each_visit.other_girls_repeat)
                chapter_totals[chapter.short_en]['repeat'] += repeat
                chapter_totals[chapter.short_en]['workshops'] += 1
                for eventattendee in EventAttendee.objects.filter(event__pk=each_visit.visit.event_ptr_id):
                    try:
                        attendance[eventattendee.user.get_full_name()]['first'] += first
                        attendance[eventattendee.user.get_full_name()]['repeat'] += repeat
                        attendance[eventattendee.user.get_full_name()]['workshops'] += 1
                    except:
                        pass
    chapter_totals[chapter.short_en]['girl_workshops'] += chapter_totals[chapter.short_en]['first'] + \
                                                          chapter_totals[chapter.short_en]['repeat']
    chapter_totals[chapter.short_en]['weighted'] = chapter_totals[chapter.short_en]['first'] + (
    float(chapter_totals[chapter.short_en]['repeat']) / 2)
    for atten in attendance:
        attendance[atten]['girl_workshops'] += attendance[atten]['first'] + attendance[atten]['repeat']
        attendance[atten]['weighted'] = attendance[atten]['first'] + (float(attendance[atten]['repeat']) / 2)
    return render_to_response('stats_global_report_breakdown.html',
                              {'chapter_totals': sorted(chapter_totals.iteritems()),
                               'attendance': sorted(attendance.iteritems(), key=lambda item: item[1]['weighted'],
                                                    reverse=True)}, context_instance=RequestContext(request))


def xint(n):
    if n is None:
        return 0
    return int(n)

