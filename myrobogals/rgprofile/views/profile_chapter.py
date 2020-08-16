"""
Views related to chapter tasks that has to do with users. For example, adding, removing, importing and exporting 
users to and from their chapter
"""

import csv
import operator
from datetime import time, date
from time import time

from django.contrib import messages
from django.contrib.admin.models import LogEntry
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import HttpResponse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import Context, loader
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _


from myrobogals.rgchapter.models import Chapter
from myrobogals.rgchapter.views import AddExecutiveForm
from myrobogals.rgmain.models import University
from myrobogals.rgmessages.models import EmailMessage, SMSMessage
from myrobogals.rgprofile.forms import EditListForm, EditStatusForm, CSVUsersUploadForm, WelcomeEmailForm, DefaultsFormOne, \
    DefaultsFormTwo
from myrobogals.rgprofile.functions import importcsv, any_exec_attr, RgImportCsvException
from myrobogals.rgprofile.models import MemberStatusType
from myrobogals.rgprofile.models import Position, PositionType
from myrobogals.rgprofile.models import User, MemberStatus
from myrobogals.rgprofile.models import UserList
from myrobogals.rgprofile.views.profile_user import edituser
from myrobogals.rgteaching.models import Event
from myrobogals.rgteaching.models import EventAttendee
from myrobogals.settings import MEDIA_URL

from myrobogals.permissionUtils import *



@login_required
def adduser(request, chapterurl):
    chapter = get_object_or_404(Chapter, myrobogals_url__exact=chapterurl)
    return edituser(request, '', chapter)


@login_required
def viewlist(request, chapterurl, list_id):
    c = get_object_or_404(Chapter, myrobogals_url__exact=chapterurl)
    if request.user.is_superuser or is_executive_or_higher(request.user, c):
        l = get_object_or_404(UserList, pk=list_id, chapter=c)
        users = l.users
        search = ''
        if 'search' in request.GET:
            search = request.GET['search']
            users = users.filter(
                Q(username__icontains=search) | Q(first_name__icontains=search) | Q(last_name__icontains=search) | Q(
                    email__icontains=search) | Q(mobile__icontains=search))
        users = users.order_by('last_name', 'first_name')
        display_columns = l.display_columns.all()

        return render_to_response('list_user_list.html',
                                  {'userlist': l, 'list_id': list_id, 'users': users, 'search': search, 'chapter': c,
                                   'display_columns': display_columns,
                                   'return': request.path + '?' + request.META['QUERY_STRING']},
                                  context_instance=RequestContext(request))
    else:
        raise Http404


@login_required
def listuserlists(request, chapterurl):
    c = get_object_or_404(Chapter, myrobogals_url__exact=chapterurl)
    uls = UserList.objects.filter(chapter=c)
    return render_to_response('list_user_lists.html', {'uls': uls, 'chapter': c},
                              context_instance=RequestContext(request))


@login_required
def adduserlist(request, chapterurl):
    return edituserlist(request, chapterurl, 0)


@login_required
def edituserlist(request, chapterurl, list_id):
    if list_id == 0:
        new = True
    else:
        new = False
    c = get_object_or_404(Chapter, myrobogals_url__exact=chapterurl)
    if request.user.is_superuser or is_executive_or_higher(request.user, chapter):
        if new:
            l = UserList()
        else:
            l = get_object_or_404(UserList, pk=list_id, chapter=c)
        if request.method == 'POST':
            ulform = EditListForm(request.POST, user=request.user)
            if ulform.is_valid():
                data = ulform.cleaned_data
                l.name = data['name']
                l.notes = data['notes']
                if new:
                    l.chapter = c
                    l.save()
                l.users = data['users']
                l.display_columns = data['display_columns']
                l.save()
                messages.success(request, message=unicode(
                    _("User list \"%(listname)s\" has been updated") % {'listname': l.name}))
                return HttpResponseRedirect('/chapters/' + chapterurl + '/lists/' + str(l.pk) + '/')
        else:
            if new:
                ulform = EditListForm(None, user=request.user)
            else:
                users_selected = []
                for u in l.users.all():
                    users_selected.append(u.pk)
                cols_selected = []
                for u in l.display_columns.all():
                    cols_selected.append(u.pk)
                ulform = EditListForm({
                    'name': l.name,
                    'users': users_selected,
                    'display_columns': cols_selected,
                    'notes': l.notes}, user=request.user)
        return render_to_response('edit_user_list.html',
                                  {'new': new, 'userlist': l, 'ulform': ulform, 'list_id': list_id, 'chapter': c},
                                  context_instance=RequestContext(request))


@login_required
def editusers(request, chapterurl):
    c = get_object_or_404(Chapter, myrobogals_url__exact=chapterurl)
    memberstatustypes = MemberStatusType.objects.all()
    if request.user.is_superuser or is_executive_or_higher(request.user, c):
        search = ''
        searchsql = ''
        if 'search' in request.GET:
            search = request.GET['search']
            search_fields = ['username', 'first_name', 'last_name', 'email', 'mobile']
            for field in search_fields:
                searchsql = searchsql + ' OR ' + field + ' LIKE "%%' + search + '%%" '
            searchsql = 'AND (' + searchsql[4:] + ')'
        if 'status' in request.GET:
            status = request.GET['status']
        else:
            status = '1'  # Default to student members

        if (status != '0'):
            users = User.objects.raw(
                'SELECT u.* FROM rgprofile_user AS u, rgprofile_memberstatus AS ms WHERE u.chapter_id ' +
                '= ' + str(
                    c.pk) + ' AND u.id = ms.user_id AND ms.statusType_id = ' + status + ' AND ms.status_date_end IS NULL ' +
                searchsql + ' ORDER BY last_name, first_name')
        else:
            users = User.objects.raw('SELECT u.* FROM rgprofile_user AS u WHERE u.chapter_id ' +
                                     '= ' + str(c.pk) + ' ' +
                                     searchsql + ' ORDER BY last_name, first_name')
        display_columns = c.display_columns.all()
        return render_to_response('user_list.html',
                                  {'memberstatustypes': memberstatustypes, 'users': users, 'numusers': len(list(users)),
                                   'search': search, 'status': int(status), 'chapter': c,
                                   'display_columns': display_columns,
                                   'return': request.path + '?' + request.META['QUERY_STRING'], 'MEDIA_URL': MEDIA_URL},
                                  context_instance=RequestContext(request))
    else:
        raise Http404


@login_required
def deleteuser(request, userpk):
    userToBeDeleted = get_object_or_404(User, pk=userpk)
    if request.user.is_superuser or is_executive_or_higher(request.user, userToBeDeleted.chapter):
        msg = ''
        old_status = userToBeDeleted.memberstatus_set.get(status_date_end__isnull=True)
        canNotDelete = False
        if Position.objects.filter(user=userToBeDeleted):
            msg = _('<br>Member "%s" has held at least one officeholder position. ') % userToBeDeleted.get_full_name()
            canNotDelete = True
        if EventAttendee.objects.filter(user=userToBeDeleted, actual_status=1):
            msg += _('<br>Member "%s" has attended at least one school visit. ') % userToBeDeleted.get_full_name()
            canNotDelete = True
        if Event.objects.filter(creator=userToBeDeleted):
            msg += _('<br>Member "%s" has created at least one school visit. ') % userToBeDeleted.get_full_name()
            canNotDelete = True
        if EmailMessage.objects.filter(sender=userToBeDeleted):
            msg += _('<br>Member "%s" has sent at least one email. ') % userToBeDeleted.get_full_name()
            canNotDelete = True
        if SMSMessage.objects.filter(sender=userToBeDeleted):
            msg += _('<br>Member "%s" has sent at least one SMS message. ') % userToBeDeleted.get_full_name()
            canNotDelete = True
        if LogEntry.objects.filter(user=userToBeDeleted):
            msg += _('<br>Member "%s" owned at least one admin log object. ') % userToBeDeleted.get_full_name()
            canNotDelete = True
        if not canNotDelete:
            if (request.method != 'POST') or (('delete' not in request.POST) and ('alumni' not in request.POST)):
                return render_to_response('user_delete_confirm.html',
                                          {'userToBeDeleted': userToBeDeleted, 'return': request.GET['return']},
                                          context_instance=RequestContext(request))
            else:
                if ('delete' in request.POST) and ('alumni' not in request.POST):
                    userToBeDeleted.delete()
                    msg = _('Member "%s" deleted') % userToBeDeleted.get_full_name()
                elif ('delete' not in request.POST) and ('alumni' in request.POST):
                    if old_status.statusType == MemberStatusType.objects.get(pk=2):
                        msg = _('Member "%s" is already marked as alumni') % userToBeDeleted.get_full_name()
                    else:
                        if userToBeDeleted.membertype().description != 'Inactive':
                            old_status.status_date_end = date.today()
                            old_status.save()
                        new_status = MemberStatus()
                        new_status.user = userToBeDeleted
                        new_status.statusType = MemberStatusType.objects.get(pk=2)
                        new_status.status_date_start = date.today()
                        new_status.save()
                        msg = _('Member "%s" marked as alumni') % userToBeDeleted.get_full_name()
                else:
                    raise Http404
        if canNotDelete:
            messages.success(request, message=unicode(
                _('- Cannot delete member. Reason(s): %s<br>Consider marking this member as alumni instead.') % msg))
        else:
            messages.success(request, message=unicode(msg))
        if 'return' in request.GET:
            return HttpResponseRedirect(request.GET['return'])
        else:
            return HttpResponseRedirect(
                '/chapters/' + request.user.chapter.myrobogals_url + '/edit/users/?search=&status=' + str(
                    old_status.statusType.pk))
    else:
        raise Http404


@login_required
def editexecs(request, chapterurl):
    chapter = get_object_or_404(Chapter, myrobogals_url__exact=chapterurl)
    if not (request.user.is_superuser or is_executive_or_higher(request.user, chapter)):
        raise Http404

    # only regional or higher can add or remove executive members
    edit_permissions = is_regional_or_higher(request.user, chapter)

    add_executive_form = None
    if edit_permissions and request.method == 'POST':
        add_executive_form = AddExecutiveForm(request.POST, chapter=chapter)
        if add_executive_form.is_valid():
            data = add_executive_form.cleaned_data
            position_type = data.get('position_type', None)
            user = data.get('user', None)

            if position_type and user:
                Position.objects.create(user=user, positionType=position_type, positionChapter=chapter, position_date_start=date.today())
                user.is_staff = True
                user.save()
            return HttpResponseRedirect("/chapters/" + chapter.myrobogals_url + "/edit/execs/")

    if edit_permissions and not add_executive_form:
        add_executive_form = AddExecutiveForm(chapter=chapter)

    officers = Position.objects.filter(positionChapter=chapter).filter(position_date_end=None).order_by('positionType__rank')

    return render_to_response('exec_list.html', {'officers': officers, 'chapter': chapter, 'add_executive_form': add_executive_form,
                                                 'edit_permissions': edit_permissions, 'return': request.path},
                              context_instance=RequestContext(request))


@login_required
def remove_exec(request, chapterurl, username):
    """
    Removes an executive, marks their position as ending today.
    """

    chapter = get_object_or_404(Chapter, myrobogals_url__exact=chapterurl)
    user = get_object_or_404(User, username__exact=username, chapter=chapter)

    if not (request.user.is_superuser or is_regional_or_higher(request.user, chapter)):
        raise Http404

    # end all current positions in this chapter
    positions = Position.objects.filter(user=user, position_date_end=None, positionChapter=chapter).update(position_date_end=date.today())

    # if user has no other positions (e.g. in global/regional), remove their is_staff flag
    other_positions = Position.objects.filter(user=user, position_date_end=None)
    if not other_positions:
        user.is_staff = False
        user.is_superuser = False
        user.save()

    messages.success(request, message=unicode(_("User %(username)s has been retired as an executive") % {'username': user.username}))

    return HttpResponseRedirect('/chapters/' + chapterurl + '/edit/execs/')


# Changing members in the chapter to a different status
@login_required
def editstatus(request, chapterurl):
    c = get_object_or_404(Chapter, myrobogals_url__exact=chapterurl)
    memberstatustypes = MemberStatusType.objects.all()
    if request.user.is_superuser or is_executive_or_higher(request.user, c):
        users = []
        if request.method == 'POST':
            ulform = EditStatusForm(request.POST, user=request.user)
            if ulform.is_valid():
                data = ulform.cleaned_data
                status = data['status']
                users = data['users']  # l:queryset
                users_already = ""
                users_changed = ""

                for user in users:
                    u = User.objects.get(username__exact=user.username)
                    old_status = u.memberstatus_set.get(status_date_end__isnull=True)
                    if old_status.statusType == MemberStatusType.objects.get(pk=int(status)):
                        if (users_already):
                            users_already = users_already + ", " + u.username
                        else:
                            users_already = u.username
                    else:
                        if user.membertype().description != 'Inactive':
                            old_status.status_date_end = date.today()
                            old_status.save()
                        new_status = MemberStatus()
                        new_status.user = u
                        new_status.statusType = MemberStatusType.objects.get(pk=int(status))
                        new_status.status_date_start = date.today()
                        new_status.save()
                        if (users_changed):
                            users_changed = users_changed + ", " + u.username
                        else:
                            users_changed = u.username

                if (users_already):
                    messages.success(request, message=unicode(
                        _("%(usernames)s are already marked as %(type)s") % {'usernames': users_already,
                                                                             'type': MemberStatusType.objects.get(
                                                                                 pk=int(status)).description}))

                if (users_changed):
                    messages.success(request, message=unicode(
                        _("%(usernames)s has/have been marked as %(type)s") % {'usernames': users_changed,
                                                                               'type': new_status.statusType.description}))

                return HttpResponseRedirect('/chapters/' + chapterurl + '/edit/users/')
            else:
                return render_to_response('edit_user_status.html',
                                          {'ulform': ulform, 'chapter': c, 'memberstatustypes': memberstatustypes},
                                          context_instance=RequestContext(request))
        else:
            ulform = EditStatusForm(None, user=request.user)
            return render_to_response('edit_user_status.html',
                                      {'ulform': ulform, 'chapter': c, 'memberstatustypes': memberstatustypes},
                                      context_instance=RequestContext(request))


@login_required
def contactdirectory(request):
    if not is_any_executive(request.user):
        raise Http404
    results = []
    name = ''
    if ('name' in request.GET) and (request.GET['name'] != ''):
        name = request.GET['name']
        for u in User.objects.filter(
                reduce(operator.or_, ((Q(first_name__icontains=x) | Q(last_name__icontains=x)) for x in name.split()))):
            if u.has_cur_pos():
                results.append(u)
    return render_to_response('contact_directory.html', {'results': results, 'name': name},
                              context_instance=RequestContext(request))


@login_required
def importusers(request, chapterurl):
    # initial value to match the default value
    chapter = get_object_or_404(Chapter, myrobogals_url__exact=chapterurl)
    if not (request.user.is_superuser or is_executive_or_higher(request.user, chapter)):
        raise Http404
    errmsg = None
    if request.method == 'POST':
        if request.POST['step'] == '1':
            form = CSVUsersUploadForm(request.POST, request.FILES)
            welcomeform = WelcomeEmailForm(request.POST, chapter=chapter)
            defaultsform1 = DefaultsFormOne(request.POST)
            defaultsform2 = DefaultsFormTwo(request.POST)
            if form.is_valid() and welcomeform.is_valid() and defaultsform1.is_valid() and defaultsform2.is_valid():
                file = request.FILES['csvfile']
                tmppath = 'tmp/' + chapter.myrobogals_url + request.user.username + '.csv'
                destination = open(tmppath, 'w')
                for chunk in file.chunks():
                    destination.write(chunk)
                destination.close()
                fp = open(tmppath, 'rU')
                filerows = csv.reader(fp)
                defaults = {}
                defaults.update(defaultsform1.cleaned_data)
                defaults.update(defaultsform2.cleaned_data)
                welcomeemail = welcomeform.cleaned_data
                cleanform = form.cleaned_data
                request.session['welcomeemail'] = welcomeemail
                request.session['defaults'] = defaults
                request.session['updateuser'] = cleanform['updateuser']
                request.session['ignore_email'] = cleanform['ignore_email']
                return render_to_response('import_users_2.html',
                                          {'tmppath': tmppath, 'filerows': filerows, 'chapter': chapter},
                                          context_instance=RequestContext(request))
        elif request.POST['step'] == '2':
            if 'tmppath' not in request.POST:
                return HttpResponseRedirect("/chapters/" + chapterurl + "/edit/users/import/")
            tmppath = request.POST['tmppath'].replace('\\\\', '\\')
            fp = open(tmppath, 'rUb')
            filerows = csv.reader(fp)

            welcomeemail = request.session['welcomeemail']
            if welcomeemail['importaction'] == '2':
                welcomeemail = None
            defaults = request.session['defaults']
            updateuser = request.session['updateuser']
            ignore_email = request.session['ignore_email']

            try:
                (users_imported, users_updated, existing_emails, error_msg) = importcsv(filerows, welcomeemail,
                                                                                        defaults, chapter, updateuser,
                                                                                        ignore_email)
            except RgImportCsvException as e:
                errmsg = e.errmsg
                return render_to_response('import_users_2.html',
                                          {'tmppath': tmppath, 'filerows': filerows, 'chapter': chapter,
                                           'errmsg': errmsg}, context_instance=RequestContext(request))

            if welcomeemail == None:
                if updateuser:
                    msg = _(
                        '%d users imported.<br>Existing usernames were found for %d rows; their details have been updated.<br>%s') % (
                              users_imported, users_updated, error_msg)
                elif ignore_email:
                    msg = _(
                        '%d users imported.<br>%d rows were ignored due to members with those email addresses already existing.<br>%s') % (
                              users_imported, existing_emails, error_msg)
                else:
                    msg = _('%d users imported.<br>%s') % (users_imported, error_msg)
            else:
                if updateuser:
                    msg = _(
                        '%d users imported and emailed.<br>Existing usernames were found for %d rows; their details have been updated.<br>%s') % (
                              users_imported, users_updated, error_msg)
                elif ignore_email:
                    msg = _(
                        '%d users imported and emailed.<br>%d rows were ignored due to members with those email addresses already existing.<br>%s') % (
                              users_imported, existing_emails, error_msg)
                else:
                    msg = _('%d users imported and emailed.<br>%s') % (users_imported, error_msg)
            messages.success(request, message=unicode(msg))
            del request.session['welcomeemail']
            del request.session['defaults']
            del request.session['updateuser']
            del request.session['ignore_email']
            return HttpResponseRedirect('/chapters/' + chapter.myrobogals_url + '/edit/users/')
    else:
        form = CSVUsersUploadForm()
        welcomeform = WelcomeEmailForm(None, chapter=chapter)
        defaultsform1 = DefaultsFormOne()
        defaultsform2 = DefaultsFormTwo()
    return render_to_response('import_users_1.html', {'chapter': chapter, 'form': form, 'welcomeform': welcomeform,
                                                      'defaultsform1': defaultsform1, 'defaultsform2': defaultsform2,
                                                      'errmsg': errmsg}, context_instance=RequestContext(request))


@login_required
def exportusers(request, chapterurl):
    c = get_object_or_404(Chapter, myrobogals_url__exact=chapterurl)
    if request.user.is_superuser or is_executive_or_higher(request.user, c):
        if 'status' in request.GET:
            status = request.GET['status']
        else:
            status = '1'  # Default to student members

        if (status != '0'):
            users = MemberStatus.objects.filter(
                user__chapter=c,
                statusType__pk=status,
                status_date_end__isnull=True
            ).values('user__username', 'user__first_name', 'user__last_name', 'user__email', 'user__mobile',
                     'user__course', 'user__university__name', 'user__student_number', 'user__alt_email',
                     'user__date_joined', 'user__dob', 'user__gender', 'user__uni_start', 'user__uni_end',
                     'user__course_type', 'user__student_type').distinct()
        else:
            users = MemberStatus.objects.filter(
                user__chapter=c,
                status_date_end__isnull=True
            ).values('user__username', 'user__first_name', 'user__last_name', 'user__email', 'user__mobile',
                     'user__course', 'user__university__name', 'user__student_number', 'user__alt_email',
                     'user__date_joined', 'user__dob', 'user__gender', 'user__uni_start', 'user__uni_end',
                     'user__course_type', 'user__student_type').distinct()

        response = HttpResponse(content_type='text/csv')
        filename = c.myrobogals_url + '-users-' + str(date.today()) + '.csv'
        response['Content-Disposition'] = 'attachment; filename=' + filename
        csv_data = (('username', 'first_name', 'last_name', 'email', 'mobile', 'course', 'university', 'student_number',
                     'alt_email', 'date_joined', 'dob', 'gender', 'uni_start', 'uni_end', 'course_type',
                     'student_type'),)
        for user in users:
            csv_data = csv_data + ((user['user__username'], user['user__first_name'], user['user__last_name'],
                                    user['user__email'], user['user__mobile'], user['user__course'],
                                    user['user__university__name'], user['user__student_number'],
                                    user['user__alt_email'], user['user__date_joined'], user['user__dob'],
                                    user['user__gender'], user['user__uni_start'], user['user__uni_end'],
                                    user['user__course_type'], user['user__student_type']),)

        t = loader.get_template('csv_export.txt')
        c = Context({
            'data': csv_data,
        })
        response.write(t.render(c))
        return response
    else:
        raise Http404


COMPULSORY_FIELDS = (
    ('first_name', 'First name'),
    ('last_name', 'Last name'),
    ('email', 'Primary email address'),
)

CREDENTIALS_FIELDS = (
    ('username',
     'myRobogals username. If blank, a username will be generated based upon their first name, last name or email address, as necessary to generate a username that is unique in the system. The new username will be included in their welcome email.'),
    ('password',
     'myRobogals password. If blank, a new password will be generated for them and included in their welcome email.'),
)

BASIC_FIELDS = (
    ('alt_email', 'Alternate email address'),
    ('mobile',
     'Mobile number, in correct local format, OR correct local format with the leading 0 missing (as Excel is prone to do), OR international format without a leading +. Examples: 61429558100 (Aus) or 447553333111 (UK)'),
    ('date_joined', 'Date when this member joined Robogals. If blank, today\'s date is used'),
    ('dob', 'Date of birth, in format 1988-10-26'),
    ('gender', '0 = No answer; 1 = Male; 2 = Female; 3 = Other'),
)

EXTRA_FIELDS = (
    ('course', 'Name of course/degree'),
    ('uni_start', 'Date when they commenced university, in format 2007-02-28'),
    ('uni_end', 'Date when they expect to complete university, in format 2011-11-30'),
    ('university_id',
     'ID of the university they attend. Enter -1 to use the host university of this Robogals chapter. <a href="unis/">Full list of university IDs</a>'),
    ('course_type', '1 = Undergraduate; 2 = Postgraduate'),
    ('student_type', '1 = Domestic student; 2 = International student'),
    ('student_number', 'Student number, a.k.a. enrolment number, candidate number, etc.'),
)

PRIVACY_FIELDS = (
    ('privacy',
     '20 = Profile viewable to public internet; 10 = Profile viewable only to Robogals members; 5 = Profile viewable only to Robogals members from same chapter; 0 = Profile viewable only to exec'),
    ('dob_public',
     'Either \'True\' or \'False\', specifies whether their date of birth should be displayed in their profile page'),
    ('email_public',
     'Either \'True\' or \'False\', specifies whether their email address should be displayed in their profile page'),
    ('email_chapter_optin',
     'Either \'True\' or \'False\', specifies whether this member will receive general emails sent by this Robogals chapter'),
    ('mobile_marketing_optin',
     'Either \'True\' or \'False\', specifies whether this member will receive general SMSes sent by this Robogals chapter'),
    ('email_reminder_optin',
     'Either \'True\' or \'False\', specifies whether this member will receive email reminders about school visits from myRobogals'),
    ('mobile_reminder_optin',
     'Either \'True\' or \'False\', specifies whether this member will receive SMS reminders about school visits from myRobogals'),
    ('email_newsletter_optin',
     'Either \'True\' or \'False\', specifies whether this member will receive The Amplifier, the monthly email newsletter of Robogals Global'),
    ('email_careers_newsletter_AU_optin',
     'Either \'True\' or \'False\', specifies whether this member will receive Robogals Careers Newsletter - Australia'),
)

HELPINFO = (
    ("Compulsory fields", COMPULSORY_FIELDS),
    ("Credentials fields", CREDENTIALS_FIELDS),
    ("Basic fields", BASIC_FIELDS),
    ("Extra fields", EXTRA_FIELDS),
    ("Privacy fields", PRIVACY_FIELDS)
)


@login_required
def importusershelp(request, chapterurl):
    chapter = get_object_or_404(Chapter, myrobogals_url__exact=chapterurl)
    if not (request.user.is_superuser or is_executive_or_higher(request.user, chapter)):
        raise Http404
    return render_to_response('import_users_help.html', {'HELPINFO': HELPINFO},
                              context_instance=RequestContext(request))


@login_required
def unilist(request, chapterurl):
    chapter = get_object_or_404(Chapter, myrobogals_url__exact=chapterurl)
    if not (request.user.is_superuser or is_executive_or_higher(request.user, chapter)):
        raise Http404
    unis = University.objects.all()
    return render_to_response('uni_ids_list.html', {'unis': unis}, context_instance=RequestContext(request))
