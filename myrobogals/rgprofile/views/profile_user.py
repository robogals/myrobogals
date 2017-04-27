"""
Views related to users signing up and editing their profile page
"""

import re
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from myrobogals.rgchapter.models import Chapter
from myrobogals.rgmessages.models import EmailMessage, SMSMessage, SMSRecipient
from myrobogals.rgmessages.models import EmailRecipient
from myrobogals.rgprofile.forms import FormPartOne, FormPartTwo, FormPartThree, \
    FormPartFour, FormPartFive, CodeOfConductForm
from myrobogals.rgprofile.forms import WelcomeEmailFormTwo
from myrobogals.rgprofile.functions import genandsendpw, RgGenAndSendPwException
from myrobogals.rgprofile.models import Position
from myrobogals.rgprofile.models import User, MemberStatus
from myrobogals.rgprofile.views.profile_login import openconductfile
from myrobogals.rgteaching.models import EventAttendee


def joinchapter(request, chapterurl):
    chapter = get_object_or_404(Chapter, myrobogals_url__exact=chapterurl)
    if chapter.is_joinable:
        if request.user.is_authenticated():
            return render_to_response('join_already_logged_in.html', {}, context_instance=RequestContext(request))
        else:
            return newuser(request, chapter)
    else:
        join_page = chapter.join_page.format(chapter=chapter)
        return render_to_response('joininfo.html', {'chapter': chapter, 'join_page': join_page},
                                  context_instance=RequestContext(request))


@login_required
def redirtoself(request):
    return HttpResponseRedirect("/profile/" + request.user.username + "/")


@login_required
def redirtoeditself(request):
    return HttpResponseRedirect("/profile/" + request.user.username + "/edit/")


def newuser(request, chapter):
    pwerr = ''
    usererr = ''
    carderr = ''
    err = []

    signup_form = FormPartOne(request.POST or None, chapter=chapter, user_id='')

    coc_form_text = openconductfile()

    if coc_form_text is not None:
        coc_form = CodeOfConductForm(request.POST or None)

    if request.method == 'POST':
        # Checks coc_form is assigned before calling is valid
        if coc_form_text is not None:
            valid_forms = signup_form.is_valid() and coc_form.is_valid()
        else:
            valid_forms = signup_form.is_valid()

        if valid_forms:
            data = signup_form.cleaned_data

            new_username = data['username']

            # Checking validity of length
            username_len = len(new_username)
            if username_len < 3:
                usererr = _('Your username must be 3 or more characters')
            elif username_len > 30:
                usererr = _('Your username must be less than 30 characters')

            # Regex check for words, letters, numbers and underscores only in username
            matches = re.compile(r'^\w+$').findall(new_username)
            if matches == []:
                usererr = _('Your username must contain only letters, numbers and underscores')

            # See if it already exists in database
            else:
                try:
                    User.objects.get(username=new_username)
                except User.DoesNotExist:
                    if request.POST['password1'] == request.POST['password2']:
                        if len(request.POST['password1']) < 5:
                            pwerr = _('Your password must be at least 5 characters long')
                        else:
                            # Creates, saves and returns a User object
                            u = User.objects.create_user(new_username, '', request.POST['password1'])
                            u.chapter = chapter
                            mt = MemberStatus(user_id=u.pk, statusType_id=1)
                            mt.save()
                            u.is_active = True
                            u.is_staff = False
                            u.is_superuser = False
                            u.code_of_conduct = True
                            if 'police_check_number' in data and 'police_check_expiration' in data:
                                u.police_check_number = data['police_check_number']
                                u.police_check_expiration = data['police_check_expiration']
                                notify_chapter(chapter, u)

                            u.save()

                            if chapter.welcome_email_enable:
                                welcome_email(request, chapter, u)

                            return HttpResponseRedirect("/welcome/" + chapter.myrobogals_url + "/")
                    else:
                        pwerr = _('The password and repeated password did not match. Please try again')
                else:
                    usererr = _('That username is already taken')

            # Compile all the errors into a list
            err = [usererr, pwerr, carderr]

    if coc_form_text is not None:
        return render_to_response('sign_up.html', {'signup_form': signup_form, 'conduct_form': coc_form, 'chapter': chapter, 'err': err}, context_instance=RequestContext(request))
    else:
        return render_to_response('sign_up.html', {'signup_form': signup_form, 'chapter': chapter, 'err': err}, context_instance=RequestContext(request))


def conduct_help(request):
    coc_form_text = openconductfile()
    return render_to_response('conduct_help.html', {'text': coc_form_text}, context_instance=RequestContext(request))


# Performs editing an existing as well as adding new user to a chapter
def edituser(request, username, chapter=None):
    pwerr = ''
    usererr = ''
    carderr = ''
    new_username = ''
    valid_card = False

    if username == '':
        join = True
        u = User()
        if request.user.is_superuser or (request.user.is_staff and request.user.chapter == chapter):
            adduser = True
        else:
            adduser = False
    else:
        join = False
        adduser = False
        if not request.user.is_authenticated():
            return HttpResponseRedirect("/login/?next=/profile/edit/")

        # Get reference to user
        u = get_object_or_404(User, username__exact=username)

        # Get user's chapter
        chapter = u.chapter

    # Either a superuser, self user or exec of chapter
    if join or request.user.is_superuser or request.user.id == u.id or (
        request.user.is_staff and request.user.chapter == u.chapter):
        # Form submission POST request
        if request.method == 'POST':
            # Obtaining the data from the post request
            formpart1 = FormPartOne(request.POST, chapter=chapter, user_id=u.id)
            formpart2 = FormPartTwo(request.POST, chapter=chapter)
            formpart3 = FormPartThree(request.POST, chapter=chapter)
            formpart4 = FormPartFour(request.POST, chapter=chapter)
            formpart5 = FormPartFive(request.POST, chapter=chapter)

            # Checking if the form is valid
            if formpart1.is_valid() and formpart2.is_valid() and formpart3.is_valid() and formpart4.is_valid() and formpart5.is_valid():
                if ('internal_notes' in request.POST) or ('trained' in request.POST) or ('security_check' in request.POST):
                    attempt_modify_exec_fields = True
                else:
                    attempt_modify_exec_fields = False

                # Clean data from form1
                data = formpart1.cleaned_data

                # Issue new username if a new user or old user changes his username
                if join or (data['username'] != '' and data['username'] != u.username):
                    new_username = data['username']

                # If new username, verify the length of the username
                if new_username:
                    username_len = len(new_username)
                    if username_len < 3:
                        usererr = _('Your username must be 3 or more characters')
                    elif username_len > 30:
                        usererr = _('Your username must be less than 30 characters')

                    # Regex check for words, letters, numbers and underscores only in username
                    matches = re.compile(r'^\w+$').findall(new_username)
                    if matches == []:
                        usererr = _('Your username must contain only letters, numbers and underscores')

                    # See if it already exists in database
                    else:
                        try:
                            usercheck = User.objects.get(username=new_username)
                        except User.DoesNotExist:
                            if join:
                                if request.POST['password1'] == request.POST['password2']:
                                    if len(request.POST['password1']) < 5:
                                        pwerr = _('Your password must be at least 5 characters long')
                                    else:
                                        # Creates, saves and returns a User object
                                        u = User.objects.create_user(new_username, '', request.POST['password1'])
                                        u.chapter = chapter
                                        mt = MemberStatus(user_id=u.pk, statusType_id=1)
                                        mt.save()
                                        u.is_active = True
                                        u.is_staff = False
                                        u.is_superuser = False

                                        if 'police_check_number' in data and 'police_check_expiration' in data:
                                            u.police_check_number = data['police_check_number']
                                            u.police_check_expiration = data['police_check_expiration']
                                            notify_chapter(chapter, u)

                                        u.save()
                                else:
                                    pwerr = _('The password and repeated password did not match. Please try again')
                        else:
                            usererr = _('That username is already taken')

                # Chapter executive accessing the profile and trying to change a password
                if request.user.is_staff and request.user != u:
                    if len(request.POST['password1']) > 0:
                        if request.POST['password1'] == request.POST['password2']:
                            # Sets the password if it's the same, doesn't save the user object
                            u.set_password(request.POST['password1'])
                        else:
                            pwerr = _('The password and repeated password did not match. Please try again')

                # No password or username errors were encountered
                if pwerr == '' and usererr == '':
                    # Form 1 data
                    data = formpart1.cleaned_data
                    u.first_name = data['first_name']
                    u.last_name = data['last_name']

                    if new_username:
                        u.username = new_username

                    username = data['username']
                    u.email = data['email']
                    u.alt_email = data['alt_email']

                    if u.mobile != data['mobile']:
                        u.mobile = data['mobile']
                        u.mobile_verified = False

                    u.gender = data['gender']

                    if 'student_number' in data:
                        u.student_number = data['student_number']
                    if 'union_member' in data:
                        u.union_member = data['union_member']
                    if 'tshirt' in data:
                        u.tshirt = data['tshirt']
                    if 'police_check_number' in data and 'police_check_expiration' in data:
                        # Send email only if the user has changed/added a police check number instead of removing
                        if data['police_check_number'] != u.police_check_number and data['police_check_expiration'] != u.police_check_expiration:
                            u.police_check_number = data['police_check_number']
                            u.police_check_expiration = data['police_check_expiration']

                            # Notify chapter of police number changes
                            notify_chapter(chapter, u)

                    # Form 2 data
                    data = formpart2.cleaned_data
                    u.privacy = data['privacy']
                    u.dob_public = data['dob_public']
                    u.email_public = data['email_public']

                    # Form 3 data
                    data = formpart3.cleaned_data
                    u.dob = data['dob']
                    u.course = data['course']
                    u.uni_start = data['uni_start']
                    u.uni_end = data['uni_end']
                    u.university = data['university']
                    u.course_type = data['course_type']
                    u.student_type = data['student_type']
                    u.job_title = data['job_title']
                    u.company = data['company']
                    u.bio = data['bio']
                    # u.job_title = data['job_title']
                    # u.company = data['company']

                    # Form 4 data
                    data = formpart4.cleaned_data
                    u.email_reminder_optin = data['email_reminder_optin']
                    u.email_chapter_optin = data['email_chapter_optin']
                    u.mobile_reminder_optin = data['mobile_reminder_optin']
                    u.mobile_marketing_optin = data['mobile_marketing_optin']
                    u.email_newsletter_optin = data['email_newsletter_optin']
                    u.email_careers_newsletter_AU_optin = data['email_careers_newsletter_AU_optin']

                    # Check whether they have permissions to edit exec only fields
                    if attempt_modify_exec_fields and (request.user.is_superuser or request.user.is_staff):
                        data = formpart5.cleaned_data
                        u.internal_notes = data['internal_notes']
                        u.trained = data['trained']
                        u.security_check = data['security_check']

                    # Save user to database
                    u.save()

                    if 'return' in request.POST:
                        # Renders successful message on page
                        messages.success(request, message=unicode(
                            _("%(username)s has been added to the chapter") % {'username': u.username}))

                        # Returns rendered page
                        return HttpResponseRedirect(request.POST['return'])

                    # If it's a new user signup
                    elif join:
                        if chapter.welcome_email_enable:
                            welcome_email(request, chapter, u)

                        # Notifies chapter of a new member the user joined on their own
                        if not adduser and chapter.notify_enable and chapter.notify_list:
                            # Sends an email to every exec on the notify list
                            message_subject = 'New user ' + u.get_full_name() + ' joined ' + chapter.name
                            message_body = 'New user ' + u.get_full_name() + ' joined ' + chapter.name + '<br/>username: ' + u.username + '<br/>full name: ' + u.get_full_name() + '<br/>email: ' + u.email
                            email_message(email_subject=message_subject, email_body=message_body, chapter=chapter)

                        # Renders welcome page
                        return HttpResponseRedirect("/welcome/" + chapter.myrobogals_url + "/")
                    else:
                        # Renders successfully updated profile message
                        messages.success(request, message=unicode(_("Profile and settings updated!")))

                        # Returns rendered page
                        return HttpResponseRedirect("/profile/" + username + "/")

        # Not POST response
        else:
            # If the user is new and joining a chapter
            if join:
                formpart1 = FormPartOne(None, chapter=chapter, user_id=0)
                formpart2 = FormPartTwo(None, chapter=chapter)
                formpart3 = FormPartThree(None, chapter=chapter)
                formpart4 = FormPartFour(None, chapter=chapter)
                formpart5 = FormPartFive(None, chapter=chapter)

            # Returning the forms with prefilled information about the user fetched from the database if editing user information
            else:
                if u.tshirt:
                    tshirt_id = u.tshirt.pk
                else:
                    tshirt_id = None

                # Data for FormPart1
                formpart1 = FormPartOne({
                    'first_name': u.first_name,
                    'last_name': u.last_name,
                    'username': u.username,
                    'email': u.email,
                    'alt_email': u.alt_email,
                    'mobile': u.mobile,
                    'gender': u.gender,
                    'student_number': u.student_number,
                    'union_member': u.union_member,
                    'police_check_number': u.police_check_number,
                    'police_check_expiration': u.police_check_expiration,
                    'tshirt': tshirt_id}, chapter=chapter, user_id=u.pk)

                # Data for FormPart2
                formpart2 = FormPartTwo({
                    'privacy': u.privacy,
                    'dob_public': u.dob_public,
                    'email_public': u.email_public}, chapter=chapter)
                if u.university:
                    uni = u.university.pk
                else:
                    uni = None
                formpart3 = FormPartThree({
                    'dob': u.dob,
                    'course': u.course,
                    'uni_start': u.uni_start,
                    'uni_end': u.uni_end,
                    'university': uni,
                    'job_title': u.job_title,
                    'company': u.company,
                    'course_type': u.course_type,
                    'student_type': u.student_type,
                    'bio': u.bio}, chapter=chapter)
                formpart4 = FormPartFour({
                    'email_reminder_optin': u.email_reminder_optin,
                    'email_chapter_optin': u.email_chapter_optin,
                    'mobile_reminder_optin': u.mobile_reminder_optin,
                    'mobile_marketing_optin': u.mobile_marketing_optin,
                    'email_newsletter_optin': u.email_newsletter_optin,
                    'email_careers_newsletter_AU_optin': u.email_careers_newsletter_AU_optin}, chapter=chapter)
                formpart5 = FormPartFive({
                    'internal_notes': u.internal_notes,
                    'trained': u.trained,
                    'security_check': u.security_check}, chapter=chapter)

        if 'return' in request.GET:
            return_url = request.GET['return']
        elif 'return' in request.POST:
            return_url = request.POST['return']
        else:
            return_url = ''

        chpass = (join or (request.user.is_staff and request.user != u))
        exec_fields = request.user.is_superuser or (request.user.is_staff and request.user.chapter == chapter)

        return render_to_response('profile_edit.html', {'join': join,
                                                        'adduser': adduser,
                                                        'chpass': chpass,
                                                        'exec_fields': exec_fields,
                                                        'formpart1': formpart1,
                                                        'formpart2': formpart2,
                                                        'formpart3': formpart3,
                                                        'formpart4': formpart4,
                                                        'formpart5': formpart5,
                                                        'u': u,
                                                        'chapter': chapter,
                                                        'usererr': usererr,
                                                        'pwerr': pwerr,
                                                        'carderr': carderr,
                                                        'new_username': new_username,
                                                        'return': return_url},
                                  context_instance=RequestContext(request))
    else:
        raise Http404  # don't have permission to change


# Shows the profile of your user
def detail(request, username):
    u = get_object_or_404(User, username__exact=username)

    # Privacy setting
    private = False
    if u.privacy >= 20:
        pass
    elif u.privacy >= 10:
        if not request.user.is_authenticated():
            private = True
    elif u.privacy >= 5:
        if not request.user.is_authenticated():
            private = True
        elif not (request.user.chapter == u.chapter):
            private = True
    else:
        if not request.user.is_authenticated():
            private = True
        elif not (request.user.chapter == u.chapter):
            private = True
        elif not request.user.is_staff:
            private = True

    if request.user.is_superuser:
        private = False

    if private:
        return render_to_response('private.html', {}, context_instance=RequestContext(request))

    current_positions = Position.objects.filter(user=u, position_date_end__isnull=True)
    past_positions = Position.objects.filter(user=u, position_date_end__isnull=False)
    account_list = list(
        set(account for account in u.aliases.all()).union(set(account for account in u.user_aliases.all())).union(set([u])))
    for account in account_list:
        subAliasesSet = set(ac for ac in account.aliases.all())
        supAliasesSet = set(ac for ac in account.user_aliases.all())
        subset = subAliasesSet.union(supAliasesSet)
        for alias in subset:
            if alias not in account_list:
                account_list.append(alias)
    visits = EventAttendee.objects.filter(user__in=account_list, actual_status=1).order_by('-event__visit_start')
    return render_to_response('profile_view.html',
                              {'user': u, 'current_positions': current_positions, 'past_positions': past_positions,
                               'visits': visits}, context_instance=RequestContext(request))


@login_required
def mobverify(request):
    if not request.user.is_staff:
        raise Http404
    if request.user.mobile_verified:
        messages.success(request, message=unicode(_('Your mobile number is already verified')))
        return HttpResponseRedirect('/profile/')
    if request.method == 'POST':
        if not request.session.get('verif_code', False):
            raise Http404
        if not request.session.get('mobile', False):
            del request.session['verif_code']
            raise Http404
        if (request.POST['verif_code'] == request.session['verif_code']) and (
                    request.user.mobile == request.session['mobile']):
            request.user.mobile_verified = True
            request.user.save()
            msg = _('Verification succeeded')
        else:
            msg = _('- Verification failed: invalid verification code')
        del request.session['verif_code']
        del request.session['mobile']
        messages.success(request, message=unicode(msg))
        return HttpResponseRedirect('/messages/sms/write/')
    else:
        if request.user.mobile:
            verif_code = User.objects.make_random_password(6)
            message = SMSMessage()
            message.body = 'Robogals verification code: ' + verif_code
            message.senderid = '61429558100'
            message.sender = User.objects.get(username='edit')
            message.chapter = Chapter.objects.get(pk=1)
            message.validate()
            message.sms_type = 1
            message.status = -1
            message.save()
            recipient = SMSRecipient()
            recipient.message = message
            recipient.user = request.user
            request.session['mobile'] = request.user.mobile
            recipient.to_number = request.session['mobile']
            recipient.save()

            # Check that we haven't used too many credits
            sms_this_month = 0
            sms_this_month_obj = SMSMessage.objects.filter(date__gte=datetime(now().year, now().month, 1, 0, 0, 0),
                                                           status__in=[0, 1])
            for obj in sms_this_month_obj:
                sms_this_month += obj.credits_used()
            sms_this_month += message.credits_used()
            if sms_this_month > Chapter.objects.get(pk=1).sms_limit:
                message.status = 3
                message.save()
                msg = _('- Verification failed: system problem please try again later')
                messages.success(request, message=unicode(msg))
                return HttpResponseRedirect('/profile/')

            message.status = 0
            message.save()
            request.session['verif_code'] = verif_code
            return render_to_response('profile_mobverify.html', {}, context_instance=RequestContext(request))
        else:
            msg = _('- Verification failed: no mobile number entered. (Profile -> Edit Profile)')
            messages.success(request, message=unicode(msg))
            return HttpResponseRedirect('/messages/sms/write/')


@login_required
def genpw(request, username):
    user = get_object_or_404(User, username__exact=username)
    chapter = user.chapter
    if not (request.user.is_superuser or (request.user.is_staff and (chapter == request.user.chapter))):
        raise Http404
    if 'return' in request.GET:
        return_url = request.GET['return']
    elif 'return' in request.POST:
        return_url = request.POST['return']
    else:
        return_url = ''
    errmsg = ''
    if request.method == 'POST':
        welcomeform = WelcomeEmailFormTwo(request.POST, chapter=chapter)
        if welcomeform.is_valid():
            welcomeemail = welcomeform.cleaned_data
            try:
                genandsendpw(user, welcomeemail, chapter)
                messages.success(request, message=unicode(_("Password generated and emailed")))
                if return_url == '':
                    return_url = '/profile/' + username + '/edit/'
                return HttpResponseRedirect(return_url)
            except RgGenAndSendPwException as e:
                errmsg = e.errmsg
    else:
        welcomeform = WelcomeEmailFormTwo(None, chapter=chapter)
    return render_to_response('genpw.html', {'welcomeform': welcomeform, 'username': user.username, 'chapter': chapter,
                                             'return': return_url, 'error': errmsg},
                              context_instance=RequestContext(request))



########################################################################################################################
# Assist functions for profile_user.py
########################################################################################################################


# Sends an email to everyone on the chapter notify list including saving message to database
def email_message(email_subject, email_body, chapter):
    message = EmailMessage()
    message.subject = email_subject
    message.body = email_body
    message.from_name = "myRobogals"
    message.from_address = "my@robogals.org"
    message.reply_address = "my@robogals.org"
    message.sender = User.objects.get(username='edit')
    message.html = True
    message.email_type = 0

    # Message is set to WAIT mode
    message.status = -1
    message.save()

    # Creates a list of all users to notify
    if chapter.notify_list != None:
        users_to_notify = chapter.notify_list.users.all()

        # Email to all users that need to be notified
        for user in users_to_notify:
            recipient = EmailRecipient()
            recipient.message = message
            recipient.user = user
            recipient.to_name = user.get_full_name()
            recipient.to_address = user.email
            recipient.save()
            message.status = 0
            message.save()


def notify_chapter(chapter, u):
    message_subject = u.get_full_name() + ' (' + u.username + ') has submitted a WWCC Number for checking'
    message_body = 'Please check the following details for ' + u.get_full_name() + ': <br /> Police check number: ' + u.police_check_number + '<br /> Expiration Date: ' + str(
        u.police_check_expiration) + '<br /> <br /> When you have verified that the volunteer has a valid card, mark them as "Passed the Police Check" on their profile from the following link: <br /> <br /> ' + 'https://myrobogals.org/profile/' + u.username + '/edit/ <br /> If they haven\'t passed the check, please re-email them at ' + u.email + ' explaining the situation'
    email_message(email_subject=message_subject, email_body=message_body, chapter=chapter)

    # Creates a new EmailMessage object preparing for an email

def welcome_email(request, chapter, u):
    message = EmailMessage()

    try:
        message.subject = chapter.welcome_email_subject.format(
            chapter=chapter,
            user=u,
            plaintext_password=request.POST['password1'])
    except Exception:
        message.subject = chapter.welcome_email_subject

    try:
        message.body = chapter.welcome_email_msg.format(
            chapter=chapter,
            user=u,
            plaintext_password=request.POST['password1'])
    except Exception:
        message.body = chapter.welcome_email_msg

    # Setting defaults
    message.from_address = 'my@robogals.org'
    message.reply_address = 'my@robogals.org'
    message.from_name = chapter.name
    message.sender = User.objects.get(username='edit')
    message.html = chapter.welcome_email_html

    # Setting message to -1 in the DB shows that the message is in WAIT mode
    message.status = -1
    message.save()

    # Prepares message for sending
    recipient = EmailRecipient()
    recipient.message = message
    recipient.user = u
    recipient.to_name = u.get_full_name()
    recipient.to_address = u.email
    recipient.save()

    # Change message to PENIDNG mode, which waits for server to send
    message.status = 0
    message.save()