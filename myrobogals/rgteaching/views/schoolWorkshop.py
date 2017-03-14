import json
import math
import urllib
import urllib2
from time import sleep

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, Paginator
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.utils.timezone import localtime, make_aware, now
from django.utils.translation import ugettext_lazy as _

from myrobogals.rgmain.models import Subdivision
from myrobogals.rgmessages.models import EmailMessage, EmailRecipient
from myrobogals.rgteaching.forms import *
from myrobogals.rgteaching.models import (DirectorySchool, Event,
                                          EventMessage, SchoolVisit, SchoolVisitStats,
                                          StarSchoolDirectory)


@login_required
def teachhome(request):
    return HttpResponseRedirect('/teaching/list/')


# View to create or edit a SchoolVisit (workshop)
@login_required
def editvisit(request, visit_id):
    chapter = request.user.chapter
    if request.user.is_staff:
        if visit_id == 0:
            v = SchoolVisit()
            v.chapter = chapter
            new = True
        else:
            v = get_object_or_404(SchoolVisit, pk=visit_id)
            new = False
        # Only allow users to see workshops from their own chapter
        if (v.chapter != chapter) and not request.user.is_superuser:
            raise Http404
        if request.method == 'POST':
            if request.user.is_superuser:
                formpart1 = SchoolVisitFormOne(request.POST, chapter=None)
            else:
                formpart1 = SchoolVisitFormOne(request.POST, chapter=chapter)
            formpart2 = SchoolVisitFormTwo(request.POST)
            formpart3 = SchoolVisitFormThree(request.POST)
            # Create or update a workshop using the validated data from the form
            if formpart1.is_valid() and formpart2.is_valid() and formpart3.is_valid():
                if visit_id == 0:  # visit_id 0 means we're creating a new one
                    v.chapter = chapter
                    v.creator = request.user
                data = formpart1.cleaned_data
                v.school = data['school']
                # Take the user's date and time input and combine it with the
                # chapter's timezone to create a timezone-aware datetime.
                v.visit_start = make_aware(datetime.datetime.combine(data['date'], data['start_time']),
                                           timezone=chapter.tz_obj())
                v.visit_end = make_aware(datetime.datetime.combine(data['date'], data['end_time']),
                                         timezone=chapter.tz_obj())
                v.location = data['location']
                v.allow_rsvp = data['allow_rsvp']

                data = formpart2.cleaned_data
                v.meeting_location = data['meeting_location']
                if data['meeting_time']:
                    v.meeting_time = make_aware(datetime.datetime.combine(data['date'], data['meeting_time']),
                                                timezone=chapter.tz_obj())
                else:
                    v.meeting_time = None
                v.contact = data['contact']
                v.contact_email = data['contact_email']
                v.contact_phone = data['contact_phone']
                data = formpart3.cleaned_data
                v.numstudents = data['numstudents']
                v.yearlvl = data['yearlvl']
                v.numrobots = data['numrobots']
                v.lessonnum = data['lessonnum']
                v.toprint = data['toprint']
                v.tobring = data['tobring']
                v.otherprep = data['otherprep']
                v.notes = data['notes']
                v.save()
                messages.success(request, message=unicode(_("School visit info updated")))
                return HttpResponseRedirect('/teaching/' + str(v.pk) + '/')
        else:
            if request.user.is_superuser:
                formchapter = None
            else:
                formchapter = chapter
            if visit_id == 0:
                formpart1 = SchoolVisitFormOne(None, chapter=formchapter)
                formpart2 = SchoolVisitFormTwo()
                formpart3 = SchoolVisitFormThree()
            else:
                # Populate the form with data from the database
                formpart1 = SchoolVisitFormOne({
                    'school': v.school,
                    'date': localtime(v.visit_start, timezone=chapter.tz_obj()).date(),
                    'start_time': localtime(v.visit_start, timezone=chapter.tz_obj()).time(),
                    'end_time': localtime(v.visit_end, timezone=chapter.tz_obj()).time(),
                    'location': v.location,
                    'school': v.school_id,
                    'allow_rsvp': v.allow_rsvp}, chapter=formchapter)

                if v.meeting_time:
                    meeting_time = localtime(v.meeting_time, timezone=chapter.tz_obj()).time()
                else:
                    meeting_time = None
                formpart2 = SchoolVisitFormTwo({
                    'meeting_location': v.meeting_location,
                    'meeting_time': meeting_time,
                    'contact': v.contact,
                    'contact_email': v.contact_email,
                    'contact_phone': v.contact_phone})
                formpart3 = SchoolVisitFormThree({
                    'numstudents': v.numstudents,
                    'yearlvl': v.yearlvl,
                    'numrobots': v.numrobots,
                    'lessonnum': v.lessonnum,
                    'toprint': v.toprint,
                    'tobring': v.tobring,
                    'otherprep': v.otherprep,
                    'notes': v.notes})

        return render_to_response('visit_edit.html',
                                  {'new': new, 'formpart1': formpart1, 'formpart2': formpart2, 'formpart3': formpart3,
                                   'chapter': chapter, 'visit_id': visit_id}, context_instance=RequestContext(request))
    else:
        raise Http404  # don't have permission to change


@login_required
def newvisit(request):
    return editvisit(request, 0)


# Create a new workshop with a school already selected.
@login_required
def newvisitwithschool(request, school_id):
    v = SchoolVisit()
    school = get_object_or_404(School, pk=school_id)
    v.chapter = request.user.chapter
    v.creator = request.user
    v.visit_start = timezone.now()
    v.visit_start.hour = 10
    v.visit_start.minute = 0
    v.visit_start.second = 0
    v.visit_end = timezone.now()
    v.visit_end.hour = 13
    v.visit_end.minute = 0
    v.visit_end.second = 0
    v.school = school
    v.location = "Enter location"
    v.save()
    return editvisit(request, v.id)


# View workshop details. This page also allows volunteers to RSVP.
@login_required
def viewvisit(request, visit_id):
    chapter = request.user.chapter
    v = get_object_or_404(SchoolVisit, pk=visit_id)
    if (v.chapter != chapter) and not request.user.is_superuser:
        raise Http404
    attended = EventAttendee.objects.filter(event=v, actual_status=1)
    attending = EventAttendee.objects.filter(event=v, rsvp_status=2)
    notattending = EventAttendee.objects.filter(event=v, rsvp_status=4)
    waitingreply = EventAttendee.objects.filter(event=v, rsvp_status=1)
    user_attended = False
    eventmessages = EventMessage.objects.filter(event=v)
    try:
        stats = SchoolVisitStats.objects.get(visit=v)
    except:
        stats = None
    try:
        ea = EventAttendee.objects.filter(event=visit_id, user=request.user)[0]
        user_rsvp_status = ea.rsvp_status
        user_attended = (ea.actual_status == 1)
    except IndexError:
        user_rsvp_status = 0
    return render_to_response('visit_view.html',
                              {'chapter': chapter, 'v': v, 'stats': stats, 'attended': attended, 'attending': attending,
                               'notattending': notattending, 'waitingreply': waitingreply,
                               'user_rsvp_status': user_rsvp_status, 'user_attended': user_attended,
                               'eventmessages': eventmessages}, context_instance=RequestContext(request))


# Creates paginator for tables greater than size 'sizeOfList'
def paginatorRender(request, listOfObjects, sizeOfList):
    visits = {}
    paginator = Paginator(listOfObjects, sizeOfList)
    page = request.GET.get('page')
    try:
        visits = paginator.page(page)
    except EmptyPage:
        visits = paginator.page(paginator.num_pages)
    except:
        visits = paginator.page(1)

    return visits


# List all workshops. Superusers will see all workshops globally; other users
# will only see their own chapter's workshops.
@login_required
def listvisits(request):
    chapter = request.user.chapter
    if request.user.is_superuser:
        schoolvisits = SchoolVisit.objects.all()
        showall = True
        chapterform = ChapterSelector(request.GET)
        visits = paginatorRender(request, schoolvisits, 75)

        if chapterform.is_valid():
            chapter_filter = chapterform.cleaned_data['chapter']
            if chapter_filter:
                schoolvisits = schoolvisits.filter(chapter=chapter_filter)
                visits = paginatorRender(request, schoolvisits, 75)
    else:
        schoolvisits = SchoolVisit.objects.filter(chapter=chapter)
        visits = paginatorRender(request, schoolvisits, 75)
        showall = False
        chapterform = None
    return render_to_response('visit_list.html',
                              {'chapterform': chapterform, 'showall': showall, 'chapter': chapter, 'visits': visits},
                              context_instance=RequestContext(request))


# Display a printable list of workshops for a given date range
@login_required
def printlistvisits(request):
    if not request.user.is_staff:
        raise Http404
    if request.method == 'POST':
        theform = VisitSelectorForm(request.POST)
        if theform.is_valid():
            formdata = theform.cleaned_data
            chapter = request.user.chapter
            # Interpret the dates as having been entered in the user's local time
            start_date = make_aware(datetime.datetime.combine(formdata['start_date'], datetime.time.min),
                                    timezone=request.user.tz_obj())
            end_date = make_aware(datetime.datetime.combine(formdata['end_date'], datetime.time.max),
                                  timezone=request.user.tz_obj())
            visits = SchoolVisit.objects.filter(visit_start__range=[start_date, end_date]).order_by('-visit_start')
            showall = True
            if not request.user.is_superuser:
                visits = visits.filter(chapter=chapter)
                showall = False
            return render_to_response('print_visit_list.html',
                                      {'showall': showall, 'chapter': chapter, 'visits': visits},
                                      context_instance=RequestContext(request))
    theform = VisitSelectorForm()
    return render_to_response('print_visit_get_range.html', {'theform': theform},
                              context_instance=RequestContext(request))


@login_required
def invitetovisit(request, visit_id):
    if not request.user.is_staff:
        raise Http404
    chapter = request.user.chapter
    v = get_object_or_404(SchoolVisit, pk=visit_id)
    error = ''
    if (v.chapter != chapter) and not request.user.is_superuser:
        raise Http404
    if request.method == 'POST':
        inviteform = InviteForm(request.POST, user=request.user, visit=v)
        if inviteform.is_valid():
            data = inviteform.cleaned_data
            try:
                if data['action'] == '1':
                    message = EmailMessage()
                    message.subject = data['subject']
                    message.body = data['body']
                    message.from_address = request.user.email
                    message.reply_address = request.user.email
                    message.sender = request.user
                    # message.html = v.chapter.invite_email_html
                    message.html = 1
                    message.from_name = chapter.name

                    # Don't send it yet until the recipient list is done
                    message.status = -1
                    # Save to database so we get a value for the primary key,
                    # which we need for entering the recipient entries
                    message.save()

                # Send to all users who haven't opted out of workshop reminders
                if request.POST['type'] == '1':
                    users = User.objects.filter(chapter=chapter, is_active=True, email_reminder_optin=True)
                # Send to chapter committee
                elif request.POST['type'] == '2':
                    users = User.objects.filter(chapter=chapter, is_active=True, is_staff=True)
                # Send to all trained users who haven't opted out of workshop reminders
                elif request.POST['type'] == '4':
                    users = User.objects.filter(chapter=chapter, is_active=True, email_reminder_optin=True,
                                                trained=True)
                # Send to a user list
                elif request.POST['type'] == '5':
                    ul = data['list']
                    users = ul.users.all()
                # Send to specifically selected users
                else:
                    users = data['memberselect']

                for one_user in users:
                    if data['action'] == '1':
                        recipient = EmailRecipient()
                        recipient.message = message
                        recipient.user = one_user
                        recipient.to_name = one_user.get_full_name()
                        recipient.to_address = one_user.email
                        recipient.save()
                    EventAttendee.objects.filter(user=one_user, event=v).delete()
                    ea = EventAttendee()
                    ea.event = v
                    ea.user = one_user
                    if data['action'] == '1':
                        ea.rsvp_status = 1
                    if data['action'] == '2':
                        ea.rsvp_status = 2
                    ea.actual_status = 0
                    ea.save()

                if data['action'] == '1':
                    # Now mark it as OK to send. The email and all recipients are now in MySQL.
                    # A background script on the server will process the queue.
                    message.status = 0
                    message.save()

                if data['action'] == '1':
                    messages.success(request,
                                     message=unicode(_("Invitations have been sent to the selected volunteers")))
                if data['action'] == '2':
                    messages.success(request, message=unicode(_("Selected volunteers have been added as attending")))
                return HttpResponseRedirect('/teaching/' + str(v.pk) + '/')
            except Exception as e:
                error = e.args[0]
    else:
        inviteform = InviteForm(None, user=request.user, visit=v)
    return render_to_response('visit_invite.html', {'inviteform': inviteform, 'visit_id': visit_id, 'error': error},
                              context_instance=RequestContext(request))


@login_required
def emailvisitattendees(request, visit_id):
    if not request.user.is_staff:
        raise Http404
    chapter = request.user.chapter
    v = get_object_or_404(SchoolVisit, pk=visit_id)
    if (v.chapter != chapter) and not request.user.is_superuser:
        raise Http404
    if request.method == 'POST':
        emailform = EmailAttendeesForm(request.POST, user=request.user, visit=v)
        if emailform.is_valid():
            data = emailform.cleaned_data

            message = EmailMessage()
            message.subject = data['subject']
            message.body = data['body']
            message.from_address = request.user.email
            message.reply_address = request.user.email
            message.sender = request.user
            message.html = True
            message.from_name = chapter.name
            message.scheduled = False

            # Don't send it yet until the recipient list is done
            message.status = -1
            # Save to database so we get a value for the primary key,
            # which we need for entering the recipient entries
            message.save()

            # Start processing recipient list
            # Send to all invitees
            if request.POST['invitee_type'] == '1':
                id_list = EventAttendee.objects.filter(event=v.id).values_list('user_id')
                users = User.objects.filter(id__in=id_list, is_active=True, email_reminder_optin=True)
            # Send to invitees who have RSVP'd as attending
            elif request.POST['invitee_type'] == '2':
                id_list = EventAttendee.objects.filter(event=v.id, rsvp_status=2).values_list('user_id')
                users = User.objects.filter(id__in=id_list, is_active=True, email_reminder_optin=True)
            # Send to invitees who have RSVP'd as not attending
            elif request.POST['invitee_type'] == '3':
                id_list = EventAttendee.objects.filter(event=v.id, rsvp_status=4).values_list('user_id')
                users = User.objects.filter(id__in=id_list, is_active=True, email_reminder_optin=True)
            # Send to invitees who have yet to RSVP
            elif request.POST['invitee_type'] == '4':
                id_list = EventAttendee.objects.filter(event=v.id, rsvp_status=1).values_list('user_id')
                users = User.objects.filter(id__in=id_list, is_active=True, email_reminder_optin=True)
            # Send to specifically selected users
            elif request.POST['invitee_type'] == '5':
                users = data['memberselect']

            for one_user in users:
                recipient = EmailRecipient()
                recipient.message = message
                recipient.user = one_user
                recipient.to_name = one_user.get_full_name()
                recipient.to_address = one_user.email
                recipient.save()

            message.status = 0
            message.save()

            messages.success(request, message=unicode(_("Email sent succesfully")))
            return HttpResponseRedirect('/teaching/' + str(v.pk) + '/')
    else:
        emailform = EmailAttendeesForm(None, user=request.user, visit=v)
    return render_to_response('visit_email.html', {'emailform': emailform, 'visit_id': visit_id},
                              context_instance=RequestContext(request))


# Cancel a workshop and send an email to all volunteers who had RSVP'd as attending
@login_required
def cancelvisit(request, visit_id):
    if not request.user.is_staff:
        raise Http404
    chapter = request.user.chapter
    v = get_object_or_404(SchoolVisit, pk=visit_id)
    if (v.chapter != chapter) and not request.user.is_superuser:
        raise Http404
    if request.method == 'POST':
        cancelform = CancelForm(request.POST, user=request.user, visit=v)
        if cancelform.is_valid():
            data = cancelform.cleaned_data
            message = EmailMessage()
            message.subject = data['subject']
            message.body = data['body']
            message.from_address = request.user.email
            message.reply_address = request.user.email
            message.sender = request.user
            message.html = True
            message.from_name = chapter.name
            message.scheduled = False

            # Don't send it yet until the recipient list is done
            message.status = -1
            # Save to database so we get a value for the primary key,
            # which we need for entering the recipient entries
            message.save()

            # Send to everyone who has been invited
            id_list = EventAttendee.objects.filter(event=v.id, rsvp_status=2).values_list('user_id')
            users = User.objects.filter(id__in=id_list, is_active=True, email_reminder_optin=True)

            for one_user in users:
                recipient = EmailRecipient()
                recipient.message = message
                recipient.user = one_user
                recipient.to_name = one_user.get_full_name()
                recipient.to_address = one_user.email
                recipient.save()

            message.status = 0
            message.save()
            Event.objects.filter(id=v.id).delete()
            messages.success(request, message=unicode(_("Visit cancelled successfully")))
            return HttpResponseRedirect('/teaching/list/')
    else:
        cancelform = CancelForm(None, user=request.user, visit=v)
    return render_to_response('visit_cancel.html', {'cancelform': cancelform, 'visit_id': visit_id},
                              context_instance=RequestContext(request))


@login_required
def dorsvp(request, event_id, user_id, rsvp_status):
    event = get_object_or_404(Event, pk=event_id)
    user = get_object_or_404(User, pk=user_id)
    if event.status != 0:
        raise Http404
    if request.user.is_staff:
        EventAttendee.objects.filter(user=user, event=event).delete()
        ea = EventAttendee(user=user, event=event, rsvp_status=rsvp_status)
        ea.save()
    elif event.chapter == user.chapter and user == request.user:
        if event.allow_rsvp == 0:  # Allow anyone to RSVP
            EventAttendee.objects.filter(user=user, event=event).delete()
            ea = EventAttendee(user=user, event=event, rsvp_status=rsvp_status)
            ea.save()
        elif event.allow_rsvp == 1:  # Only allow invitees to RSVP
            if EventAttendee.objects.filter(user=user, event=event).count() > 0:
                EventAttendee.objects.filter(user=user, event=event).delete()
                ea = EventAttendee(user=user, event=event, rsvp_status=rsvp_status)
                ea.save()
    return HttpResponseRedirect('/teaching/' + str(event.pk) + '/')


# RSVP to a workshop, with the option to leave a message
def rsvp(request, event_id, user_id, rsvp_type):
    e = get_object_or_404(Event, pk=event_id)
    chapter = request.user.chapter
    if rsvp_type == 'yes':
        rsvp_id = 2
        rsvp_string = _("RSVP'd as attending")
        title_string = _("RSVP as attending")
    elif rsvp_type == 'no':
        rsvp_id = 4
        rsvp_string = _("RSVP'd as not attending")
        title_string = _("RSVP as not attending")
    elif rsvp_type == 'remove':
        title_string = _("Remove an invitee")
        rsvp_string = _("Removed from this event")
        rsvp_id = 0
    else:
        raise Http404
    if e.chapter != chapter and not request.user.is_superuser:
        raise Http404
    if request.method == 'POST':
        rsvpform = RSVPForm(request.POST, user=request.user, event=e)
        if rsvpform.is_valid():
            data = rsvpform.cleaned_data
            if data['leave_message'] == True:
                rsvpmessage = EventMessage()
                rsvpmessage.event = e
                rsvpmessage.user = request.user
                rsvpmessage.date = now()
                rsvpmessage.message = data['message']
                rsvpmessage.save()
            messages.success(request, message=unicode(rsvp_string))
            return dorsvp(request, event_id, user_id, rsvp_id)
    else:
        rsvpform = RSVPForm(None, user=request.user, event=e)
    return render_to_response('event_rsvp.html',
                              {'rsvpform': rsvpform, 'title_string': title_string, 'event_id': event_id,
                               'user_id': user_id, 'rsvp_type': rsvp_type}, context_instance=RequestContext(request))


# Delete an RSVP message from the workshop
@login_required
def deletemessage(request, visit_id, message_id):
    if not request.user.is_staff:
        raise Http404
    chapter = request.user.chapter
    v = get_object_or_404(Event, pk=visit_id)
    m = get_object_or_404(EventMessage, pk=message_id)
    if (v.chapter != chapter) and not request.user.is_superuser:
        raise Http404
    if request.user.is_staff:
        m.delete()
        messages.success(request, message=unicode(_("Message deleted")))
    else:
        raise Http404
    return HttpResponseRedirect('/teaching/' + str(v.pk) + '/')


# View to enter stats. This workflow contains two pages:
#  1. Select the type of visit, enter number of students, and select volunteers who attended
#  2. Select how many hours each volunteer attended
@login_required
def stats(request, visit_id):
    v = get_object_or_404(SchoolVisit, pk=visit_id)
    if v.school.chapter != request.user.chapter and not request.user.is_superuser:
        raise Http404
    if not request.user.is_staff:
        raise Http404
    if v.status != 0:
        messages.success(request, message=unicode(_("- This workshop is already closed")))
        return HttpResponseRedirect('/teaching/' + str(v.pk) + '/')
    if not request.session.get('hoursPerPersonStage', False):
        # Page 1: show stats form
        request.session['hoursPerPersonStage'] = 1
        form = SchoolVisitStatsForm(None, visit=v)
        return render_to_response('visit_stats.html', {'form': form, 'visit_id': visit_id},
                                  context_instance=RequestContext(request))
    if request.method == 'POST' and request.session['hoursPerPersonStage'] == 1:
        # Post from page 1: save entered stats into database
        request.session['hoursPerPersonStage'] = 2
        form = SchoolVisitStatsForm(request.POST, visit=v)
        if form.is_valid():
            data = form.cleaned_data
            # Delete any existing stats that may exist for this visit.
            # This can happen if the user clicks back after entering stats
            # to change their stats
            v.schoolvisitstats_set.all().delete()
            # and add the new stats just entered
            stats = SchoolVisitStats()
            stats.visit = v
            stats.visit_type = data['visit_type']
            stats.primary_girls_first = data['primary_girls_first']
            stats.primary_girls_repeat = data['primary_girls_repeat']
            stats.primary_boys_first = data['primary_boys_first']
            stats.primary_boys_repeat = data['primary_boys_repeat']
            stats.high_girls_first = data['high_girls_first']
            stats.high_girls_repeat = data['high_girls_repeat']
            stats.high_boys_first = data['high_boys_first']
            stats.high_boys_repeat = data['high_boys_repeat']
            stats.other_girls_first = data['other_girls_first']
            stats.other_girls_repeat = data['other_girls_repeat']
            stats.other_boys_first = data['other_boys_first']
            stats.other_boys_repeat = data['other_boys_repeat']
            stats.notes = data['notes']
            stats.save()

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
            return render_to_response('visit_hoursPerPerson.html', {'attended': data['attended'], 'visit_id': visit_id,
                                                                    'defaultHours': range(defaultHours)},
                                      context_instance=RequestContext(request))
        else:
            request.session['hoursPerPersonStage'] = 1
            return render_to_response('visit_stats.html', {'form': form, 'visit_id': visit_id},
                                      context_instance=RequestContext(request))
    elif request.method == 'POST' and request.session['hoursPerPersonStage'] == 2:
        raise Http404   # TODO: double check, get 2 when pressing back on page 2
    else:
        request.session['hoursPerPersonStage'] = 1
        form = SchoolVisitStatsForm(None, visit=v)
        return render_to_response('visit_stats.html', {'form': form, 'visit_id': visit_id},
                                  context_instance=RequestContext(request))


# Delete stats associated with a visit, and set it back to "open"
@login_required
def reopenvisit(request, visit_id):
    v = get_object_or_404(SchoolVisit, pk=visit_id)
    if v.school.chapter != request.user.chapter and not request.user.is_superuser:
        raise Http404
    if not request.user.is_staff:
        raise Http404
    if v.status != 1:
        messages.success(request, message=unicode(_("- This workshop is already open!")))
        return HttpResponseRedirect('/teaching/' + str(v.pk) + '/')
    # Don't allow modifying of RRR stats - too many people have access
    if v.school.chapter.myrobogals_url == 'rrr' and not request.user.is_superuser:
        messages.success(request, message=unicode(
            _("- To modify stats for Robogals Rural & Regional please contact support@robogals.org")))
        return HttpResponseRedirect('/teaching/' + str(v.pk) + '/')
    # Don't allow modifying of stats more than 1 months old - to limit damage in cases of misuse
    if (timezone.now() - v.visit_start) > datetime.timedelta(days=30):
        messages.success(request, message=unicode(_(
            "- To protect against accidental deletion of old stats, workshops more than six months old cannot be re-opened. If you need to amend these stats please contact support@robogals.org")))
        return HttpResponseRedirect('/teaching/' + str(v.pk) + '/')
    if 'confirm' in request.GET:
        if request.GET['confirm'] == '1':
            v.schoolvisitstats_set.all().delete()
            v.status = 0
            v.save()
            messages.success(request, message=unicode(_("Stats deleted and workshop re-opened.")))
            return HttpResponseRedirect('/teaching/' + str(visit_id) + '/')
        else:
            # Someone has set a random value for &confirm=
            raise Http404
    else:
        return render_to_response('visit_reopen.html', {'visit_id': visit_id}, context_instance=RequestContext(request))


# Enter the number of hours volunteered by each volunteer
@login_required
def statsHoursPerPerson(request, visit_id):
    v = get_object_or_404(SchoolVisit, pk=visit_id)
    if v.school.chapter != request.user.chapter and not request.user.is_superuser:
        raise Http404
    if not request.user.is_staff:
        raise Http404
    if not request.session.get('hoursPerPersonStage', False):
        raise Http404
    if request.method == 'POST' and request.session['hoursPerPersonStage'] == 2:
        del request.session['hoursPerPersonStage']
        for person in EventAttendee.objects.filter(event__id=v.id):
            if str(person.user.pk) in request.POST.keys():
                person.hours = request.POST[str(person.user.pk)]
                person.actual_status = 1
                person.save()
            else:
                person.hours = 0
                person.actual_status = 2
                person.save()
        v.status = 1
        v.save()
        messages.success(request, message=unicode(_("Stats saved successfully, visit closed.")))
        return HttpResponseRedirect('/teaching/' + str(v.pk) + '/')
    else:
        raise Http404


# Delete a school. A school can only be deleted if it has no workshops.
@login_required
def deleteschool(request, school_id):
    if not request.user.is_staff:
        raise Http404
    chapter = request.user.chapter
    s = get_object_or_404(School, pk=school_id)
    if (s.chapter != chapter):
        raise Http404
    if request.method == 'POST':
        deleteform = DeleteForm(request.POST, user=request.user, school=s)
        if SchoolVisit.objects.filter(school=s):
            messages.success(request,
                             message=unicode(_("You cannot delete this school as it has a workshop in the database.")))
            return HttpResponseRedirect('/teaching/schools/')
        else:
            School.objects.filter(id=s.id).delete()
            messages.success(request, message=unicode(_("School sucessfully deleted.")))
            return HttpResponseRedirect('/teaching/schools/')
    else:
        deleteform = DeleteForm(None, user=request.user, school=s)
    return render_to_response('school_delete.html', {'school': s}, context_instance=RequestContext(request))


# List all this chapter's schools
@login_required
def listschools(request):
    if not request.user.is_staff:
        raise Http404
    chapter = request.user.chapter
    schools = School.objects.filter(chapter=chapter)
    return render_to_response('schools_list.html', {'chapter': chapter, 'schools': schools},
                              context_instance=RequestContext(request))


# Populate latitude-longitude in schools directory by converting the address using a Google API
@login_required
def filllatlngschdir(request):
    if request.user.is_superuser:
        schools = DirectorySchool.objects.all()
        over_query_limit = False
        for school in schools:
            sleep(0.1)
            if (school.latitude == None) or (school.longitude == None):
                data = {}
                data['address'] = school.address_street
                data[
                    'components'] = '|locality:' + school.address_city + '|administrative_area:' + school.state_code() + '|country:' + school.address_country_id + '|postal_code:' + school.address_postcode
                data['sensor'] = 'false'
                url_values = urllib.urlencode(data)
                url = 'http://maps.googleapis.com/maps/api/geocode/json'
                full_url = url + '?' + url_values
                data = urllib2.urlopen(full_url, timeout=2)
                result = json.loads(data.read())
                if result['status'] == 'OK':
                    school.latitude = result['results'][0]['geometry']['location']['lat']
                    school.longitude = result['results'][0]['geometry']['location']['lng']
                    school.save()
                elif result['status'] == 'ZERO_RESULTS':
                    pass
                elif result['status'] == 'OVER_QUERY_LIMIT':
                    msg = '- You have reached one day quota!'
                    over_query_limit = True
                    break
                elif result['status'] == 'REQUEST_DENIED':
                    pass
                elif result['status'] == 'INVALID_REQUEST':
                    pass
                else:
                    pass
            else:
                pass
        if not over_query_limit:
            msg = 'Operation successful!'
    else:
        msg = '- You can not do this!'
    messages.success(request, message=unicode(msg))
    return render_to_response('response.html', {}, context_instance=RequestContext(request))


# Schools directory. This is populated in bulk to allow Robogals chapters
# to look up schools in their area.
@login_required
def schoolsdirectory(request, chapterurl):
    c = get_object_or_404(Chapter, myrobogals_url__exact=chapterurl)
    if not request.user.is_superuser and (not request.user.is_staff or request.user.chapter != c):
        raise Http404
    schools_list = DirectorySchool.objects.all()
    name = ''
    suburb = ''
    school_type = '-1'
    school_level = '-1'
    school_gender = '-1'
    starstatus = '-1'
    distance = ''
    origin = ''
    state = '1'
    if ('name' in request.GET) and (request.GET['name'] != ''):
        name = request.GET['name']
        schools_list = schools_list.filter(name__icontains=request.GET['name'])
    if ('suburb' in request.GET) and (request.GET['suburb'] != ''):
        suburb = request.GET['suburb']
        schools_list = schools_list.filter(address_city__icontains=request.GET['suburb'])
    if ('type' in request.GET) and (request.GET['type'] != '-1'):
        school_type = request.GET['type']
        schools_list = schools_list.filter(type=school_type)
    if ('level' in request.GET) and (request.GET['level'] != '-1'):
        school_level = request.GET['level']
        schools_list = schools_list.filter(level=school_level)
    if ('gender' in request.GET) and (request.GET['gender'] != '-1'):
        school_gender = request.GET['gender']
        schools_list = schools_list.filter(gender=school_gender)
    star_schools = StarSchoolDirectory.objects.filter(chapter=c).values_list('school_id', flat=True)
    if ('starstatus' in request.GET) and (request.GET['starstatus'] != '-1'):
        starstatus = request.GET['starstatus']
        if starstatus == '1':
            schools_list = schools_list.filter(id__in=star_schools)
        else:
            schools_list = schools_list.exclude(id__in=star_schools)
    sch_list = {}
    L1 = None
    G1 = None
    if ('distance' in request.GET) and (request.GET['distance'] != '') and ('origin' in request.GET) and (
        request.GET['origin'] != '') and ('state' in request.GET):
        distance = float(request.GET['distance'])
        origin = request.GET['origin']
        state = request.GET['state']
        subdiv = get_object_or_404(Subdivision, pk=state)
        try:
            data = {}
            data[
                'components'] = 'locality:' + origin + '|administrative_area:' + subdiv.code + '|country:' + subdiv.country.pk
            data['sensor'] = 'false'
            url_values = urllib.urlencode(data)
            url = 'http://maps.googleapis.com/maps/api/geocode/json'
            full_url = url + '?' + url_values
            data = urllib2.urlopen(full_url, timeout=2)
            result = json.loads(data.read())
            if result['status'] == 'OK':
                L1 = float(result['results'][0]['geometry']['location']['lat'])
                G1 = float(result['results'][0]['geometry']['location']['lng'])
                for school in schools_list:
                    if (school.latitude != None) and (school.longitude != None):
                        L2 = school.latitude
                        G2 = school.longitude
                        DG = G2 - G1
                        PI = 3.141592654
                        # Great-circle distance
                        D = 1.852 * 60.0 * (180.0 / PI) * math.acos(
                            math.sin(math.radians(L1)) * math.sin(math.radians(L2)) + math.cos(
                                math.radians(L1)) * math.cos(math.radians(L2)) * math.cos(math.radians(DG)))
                        if D <= distance:
                            sch_list[school.id] = D
                sch_list_sorted_keys = sorted(sch_list, key=sch_list.get)
                l = []
                for key in sch_list_sorted_keys:
                    l.append(schools_list.get(pk=key))
                schools_list = l
            else:
                schools_list = schools_list.filter(address_state=subdiv, address_city__iexact=origin)
                messages.success(request, message=unicode(_(
                    '- Sorry, suburb coordinate cannot be retrieved! Instead, schools within the same suburb are displayed.')))
        except:
            schools_list = schools_list.filter(address_state=subdiv, address_city__iexact=origin)
            messages.success(request, message=unicode(_(
                '- Sorry, suburb coordinate cannot be retrieved! Instead, schools within the same suburb are displayed')))

    schools = paginatorRender(request, schools_list, 26)
    copied_schools = School.objects.filter(chapter=c).values_list('name', flat=True)
    return render_to_response('schools_directory.html',
                              {'schools': schools, 'subdivision': Subdivision.objects.all().order_by('id'),
                               'DirectorySchool': DirectorySchool, 'name': name, 'suburb': suburb,
                               'school_type': int(school_type), 'school_level': int(school_level),
                               'school_gender': int(school_gender), 'starstatus': int(starstatus), 'state': int(state),
                               'star_schools': star_schools, 'chapterurl': chapterurl,
                               'return': request.path + '?' + request.META['QUERY_STRING'],
                               'copied_schools': copied_schools, 'distance': distance, 'origin': origin,
                               'sch_list': sch_list, 'L1': L1, 'G1': G1}, context_instance=RequestContext(request))


# Enable the 'star' next to a school in the schools directory
# Schools are 'starred' on a chapter-specific basis
@login_required
def starschool(request):
    if ('school_id' in request.GET) and ('chapterurl' in request.GET):
        s = get_object_or_404(DirectorySchool, pk=request.GET['school_id'])
        c = get_object_or_404(Chapter, myrobogals_url__exact=request.GET['chapterurl'])
        if not request.user.is_superuser and (not request.user.is_staff or request.user.chapter != c):
            raise Http404
        if StarSchoolDirectory.objects.filter(school=s, chapter=c):
            msg = '- The school "' + s.name + '" has been starred'
        else:
            starSchool = StarSchoolDirectory()
            starSchool.school = s
            starSchool.chapter = c
            starSchool.save()
            msg = 'The school "' + s.name + '" is starred'
        messages.success(request, message=unicode(_(msg)))
        if 'return' in request.GET:
            return HttpResponseRedirect(request.GET['return'])
        elif 'return' in request.POST:
            return HttpResponseRedirect(request.POST['return'])
        else:
            return HttpResponseRedirect('/teaching/schoolsdirectory/' + c.myrobogals_url)
    else:
        raise Http404


# Disable the 'star' next to a school in the schools directory
# Schools are 'starred' on a chapter-specific basis
@login_required
def unstarschool(request):
    if ('school_id' in request.GET) and ('chapterurl' in request.GET):
        s = get_object_or_404(DirectorySchool, pk=request.GET['school_id'])
        c = get_object_or_404(Chapter, myrobogals_url__exact=request.GET['chapterurl'])
        if not request.user.is_superuser and (not request.user.is_staff or request.user.chapter != c):
            raise Http404
        starschools = StarSchoolDirectory.objects.filter(school=s, chapter=c)
        if starschools:
            for starschool in starschools:
                starschool.delete()
            msg = 'The school "' + s.name + '" is unstarred'
        else:
            msg = '- The school "' + s.name + '" is not starred'
        messages.success(request, message=unicode(_(msg)))
        if 'return' in request.GET:
            return HttpResponseRedirect(request.GET['return'])
        elif 'return' in request.POST:
            return HttpResponseRedirect(request.POST['return'])
        else:
            return HttpResponseRedirect('/teaching/schoolsdirectory/' + c.myrobogals_url)
    else:
        raise Http404


# Copy a school from the schools directory into the chapter's school list
@login_required
def copyschool(request):
    if ('school_id' in request.GET) and ('chapterurl' in request.GET):
        s = get_object_or_404(DirectorySchool, pk=request.GET['school_id'])
        c = get_object_or_404(Chapter, myrobogals_url__exact=request.GET['chapterurl'])
        if not request.user.is_superuser and (not request.user.is_staff or request.user.chapter != c):
            raise Http404
        if School.objects.filter(chapter=c, name=s.name).count() > 0:
            msg = '- The school "' + s.name + '" is already already in your schools list'
        else:
            school = School()
            school.name = s.name
            school.chapter = c
            school.address_street = s.address_street
            school.address_city = s.address_city
            school.address_state = s.address_state.code
            school.address_postcode = s.address_postcode
            school.address_country = s.address_country
            school.contact_email = s.email
            school.contact_phone = s.phone
            school.save()
            msg = 'The school "' + s.name + '" has been added to your schools list. You can now create a workshop at this school.'
        messages.success(request, message=unicode(_(msg)))
        if 'return' in request.GET:
            return HttpResponseRedirect(request.GET['return'])
        elif 'return' in request.POST:
            return HttpResponseRedirect(request.POST['return'])
        else:
            return HttpResponseRedirect('/teaching/schoolsdirectory/' + c.myrobogals_url)
    else:
        raise Http404


# View to edit a school, or add a school if called with school_id = 0
@login_required
def editschool(request, school_id):
    chapter = request.user.chapter
    if request.user.is_staff:
        if school_id == 0:
            s = School()
            s.chapter = chapter
            new = True
        else:
            s = get_object_or_404(School, pk=school_id)
            new = False
        if (s.chapter != chapter):
            raise Http404
        if request.method == 'POST':
            formpart1 = SchoolFormPartOne(request.POST, chapter=chapter, school_id=school_id)
            formpart2 = SchoolFormPartTwo(request.POST)
            formpart3 = SchoolFormPartThree(request.POST)
            if formpart1.is_valid() and formpart2.is_valid() and formpart3.is_valid():
                if school_id == 0:
                    s.chapter = chapter
                    s.creator = request.user
                data = formpart1.cleaned_data
                s.name = data['name']
                s.address_street = data['address_street']
                s.address_city = data['address_city']
                s.address_state = data['address_state']
                s.address_postcode = data['address_postcode']
                s.address_country = data['address_country']
                data = formpart2.cleaned_data
                s.contact_person = data['contact_person']
                s.contact_position = data['contact_position']
                s.contact_email = data['contact_email']
                s.contact_phone = data['contact_phone']
                data = formpart3.cleaned_data
                s.notes = data['notes']
                s.save()
                messages.success(request, message=unicode(_("School info updated")))
                return HttpResponseRedirect('/teaching/schools/')
        else:
            if school_id == 0:
                formpart1 = SchoolFormPartOne(None, chapter=chapter, school_id=school_id)
                formpart2 = SchoolFormPartTwo()
                formpart3 = SchoolFormPartThree()
            else:
                formpart1 = SchoolFormPartOne({
                    'name': s.name,
                    'address_street': s.address_street,
                    'address_city': s.address_city,
                    'address_state': s.address_state,
                    'address_postcode': s.address_postcode,
                    'address_country': s.address_country.pk}, chapter=chapter, school_id=school_id)
                formpart2 = SchoolFormPartTwo({
                    'contact_person': s.contact_person,
                    'contact_position': s.contact_position,
                    'contact_email': s.contact_email,
                    'contact_phone': s.contact_phone})
                formpart3 = SchoolFormPartThree({
                    'notes': s.notes})

        return render_to_response('school_edit.html',
                                  {'new': new, 'formpart1': formpart1, 'formpart2': formpart2, 'formpart3': formpart3,
                                   'chapter': chapter, 'school_id': school_id},
                                  context_instance=RequestContext(request))
    else:
        raise Http404  # don't have permission to change


@login_required
def newschool(request):
    return editschool(request, 0)


# Display a page showing an explanation of the different stats categories
@login_required
def statshelp(request):
    if not request.user.is_staff:
        raise Http404
    return render_to_response('visit_stats_help.html', {}, context_instance=RequestContext(request))
