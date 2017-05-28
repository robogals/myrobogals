import datetime

from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from tinymce.widgets import TinyMCE

from myrobogals.rgchapter.models import Chapter
from myrobogals.rgmain.models import Country
from myrobogals.rgmain.utils import SelectDateWidget
from myrobogals.rgprofile.models import MemberStatus, User, UserList
from myrobogals.rgteaching.models import (VISIT_TYPES_BASE, VISIT_TYPES_REPORT,
                                          EventAttendee, School)


# Base class for SchoolVisitForm
class SchoolVisitFormOneBase(forms.Form):
    school = forms.ModelChoiceField(queryset=School.objects.none(), help_text=_(
        'If the school is not listed here, it first needs to be added in Workshops > Add School'))
    date = forms.DateField(label=_('School visit date'),
                           widget=SelectDateWidget(years=range(2008, datetime.date.today().year + 3)),
                           initial=timezone.now().date())
    start_time = forms.TimeField(label=_('Start time'), initial='10:00:00')
    end_time = forms.TimeField(label=_('End time'), initial='13:00:00')
    location = forms.CharField(label=_("Location"), help_text=_("Where the workshop takes place, at the school or elsewhere"))

    # Form validation
    def clean(self):
        cleaned_data = super(SchoolVisitFormOneBase, self).clean()
        start = cleaned_data.get("start_time")
        end = cleaned_data.get("end_time")
        if start and end and end <= start:
            msg = _("Start time must be before end time.")
            self._errors["start_time"] = self.error_class([msg])
            self._errors["end_time"] = self.error_class([msg])
            del cleaned_data["start_time"]
            del cleaned_data["end_time"]
        return cleaned_data


# Forms to create or edit a SchoolVisit (regular workshop)
class SchoolVisitFormOne(SchoolVisitFormOneBase):
    ALLOW_RSVP_CHOICES = (
        (0, 'Allow anyone to RSVP'),
        (1, 'Only allow invitees to RSVP'),
        (2, 'Do not allow anyone to RSVP'),
    )

    allow_rsvp = forms.ChoiceField(label=_("Allowed RSVPs"), choices=ALLOW_RSVP_CHOICES, initial=0)

    # Here we override the constructor so that the school drop-down menu will only be
    # populated with this chapter's schools
    def __init__(self, *args, **kwargs):
        chapter = kwargs.pop('chapter')
        super(SchoolVisitFormOne, self).__init__(*args, **kwargs)
        if chapter == None:
            self.fields["school"].queryset = School.objects.all().order_by('name')
        else:
            self.fields["school"].queryset = School.objects.filter(chapter=chapter).order_by('name')

            self.fields["location"].help_text += ", (can differ from meeting location, see below)"



# Form to create or edit a InstantSchoolVisit (instant workshop)
class SchoolVisitFormInstant(SchoolVisitFormOneBase):
    school = forms.ChoiceField(choices=[(school.id, school) for school in School.objects.all()],
                               widget=forms.Select(attrs={'onchange': 'NewSchoolSelect();'}))

    def __init__(self, *args, **kwargs):
        chapter = kwargs.pop('chapter')
        super(SchoolVisitFormInstant, self).__init__(*args, **kwargs)

        if chapter is None:
            school_query_set = School.objects.all().order_by('name')
        else:
            school_query_set = School.objects.filter(chapter=chapter).order_by('name')

        query_set_tuple = [(q, q) for q in school_query_set]
        self.fields['school'].choices = query_set_tuple + [('-1', '--------------'), ('0', 'New School')]



class SchoolVisitFormTwo(forms.Form):
    meeting_location = forms.CharField(label=_("Meeting location"), help_text=_(
        "Where people will meet at university to go as a group to the school, if applicable"), initial=_("N/A"),
                                       required=False)
    meeting_time = forms.TimeField(label=_("Meeting time"),
                                   help_text=_("What time people can meet to go to the school"), initial="09:30:00",
                                   required=False)
    contact = forms.CharField(label=_("Contact person"), max_length=128, required=False)
    contact_email = forms.CharField(label=_("Email"), max_length=128, required=False)
    contact_phone = forms.CharField(label=_("Phone"), max_length=32, required=False,
                                    help_text=_("Mobile number to call if people get lost"))


class SchoolVisitFormThree(forms.Form):
    numstudents = forms.CharField(label=_("Expected number of students"), required=False)
    yearlvl = forms.CharField(label=_("Year level"), required=False)
    numrobots = forms.CharField(label=_("Number of robots to bring"), required=False)
    lessonnum = forms.CharField(label=_("Lesson number"), required=False)
    toprint = forms.CharField(label=_("To print"), required=False,
                              widget=forms.Textarea(attrs={'cols': '35', 'rows': '7'}))
    tobring = forms.CharField(label=_("To bring"), required=False,
                              widget=forms.Textarea(attrs={'cols': '35', 'rows': '7'}))
    otherprep = forms.CharField(label=_("Other preparation"), required=False,
                                widget=forms.Textarea(attrs={'cols': '35', 'rows': '7'}))
    notes = forms.CharField(label=_("Other notes"), required=False,
                            widget=forms.Textarea(attrs={'cols': '35', 'rows': '7'}))


# Chapter selector for superusers viewing the workshop list
class ChapterSelector(forms.Form):
    chapter = forms.ModelChoiceField(queryset=Chapter.objects.filter(status__in=[0, 2]), required=False)


class VisitSelectorForm(forms.Form):
    start_date = forms.DateField(label='Start date',
                                 widget=SelectDateWidget(years=range(2008, datetime.date.today().year + 1)),
                                 initial=timezone.now().date())
    end_date = forms.DateField(label='End date',
                               widget=SelectDateWidget(years=range(2008, datetime.date.today().year + 1)),
                               initial=timezone.now().date())


class EmailModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return obj.last_name + ", " + obj.first_name


# Invite or add volunteers to a workshop
class InviteForm(forms.Form):
    subject = forms.CharField(max_length=256, required=False)
    body = forms.CharField(widget=TinyMCE(attrs={'cols': 70}), required=False)
    memberselect = EmailModelMultipleChoiceField(queryset=User.objects.none(),
                                                 widget=FilteredSelectMultiple(_("Recipients"), False,
                                                                               attrs={'rows': 10}), required=False)
    list = forms.ModelChoiceField(queryset=UserList.objects.none(), required=False)
    action = forms.ChoiceField(choices=((1, _('Invite members')), (2, _('Add members as attending'))), initial=1)

    # Override the constructor to show this chapter's users, user lists, and email template
    def __init__(self, *args, **kwargs):
        user = kwargs['user']
        del kwargs['user']
        visit = kwargs['visit']
        del kwargs['visit']
        super(InviteForm, self).__init__(*args, **kwargs)
        self.fields['memberselect'].queryset = User.objects.filter(chapter=user.chapter, is_active=True,
                                                                   email_reminder_optin=True,
                                                                   pk__in=MemberStatus.objects.filter(statusType__pk=1,
                                                                                                      status_date_end__isnull=True).values_list(
                                                                       'user_id', flat=True)).order_by('last_name')
        self.fields['list'].queryset = UserList.objects.filter(chapter=user.chapter)
        if visit.chapter.invite_email_subject:
            self.fields['subject'].initial = visit.chapter.invite_email_subject
        if visit.chapter.invite_email_msg:
            try:
                self.fields['body'].initial = visit.chapter.invite_email_msg.format(visit=visit, user=user)
            except Exception:
                self.fields['body'].initial = ""


# Form to email workshop attendees	
class EmailAttendeesForm(forms.Form):
    SCHEDULED_DATE_TYPES = (
        (1, 'My timezone'),
        (2, 'Recipients\' timezones'),
    )

    subject = forms.CharField(max_length=256, required=False)
    body = forms.CharField(widget=TinyMCE(attrs={'cols': 70}), required=False)
    memberselect = EmailModelMultipleChoiceField(queryset=User.objects.none(),
                                                 widget=FilteredSelectMultiple(_("Recipients"), False,
                                                                               attrs={'rows': 10}), required=False)

    # Override the constructor so that only users who have been invited are shown in the user selector
    def __init__(self, *args, **kwargs):
        user = kwargs['user']
        del kwargs['user']
        visit = kwargs['visit']
        del kwargs['visit']
        super(EmailAttendeesForm, self).__init__(*args, **kwargs)
        id_list = EventAttendee.objects.filter(event=visit.id).values_list('user_id')
        self.fields['memberselect'].queryset = User.objects.filter(id__in=id_list, is_active=True,
                                                                   email_reminder_optin=True).order_by('last_name')


class CancelForm(forms.Form):
    subject = forms.CharField(max_length=256, required=False, widget=forms.TextInput(attrs={'size': '40'}))
    body = forms.CharField(widget=TinyMCE(attrs={'cols': 70}), required=False)

    # Override the constructor to insert an email message specific to this workshop
    def __init__(self, *args, **kwargs):
        user = kwargs['user']
        del kwargs['user']
        visit = kwargs['visit']
        del kwargs['visit']
        super(CancelForm, self).__init__(*args, **kwargs)
        self.fields['subject'].initial = _("Robogals workshop for %(school)s cancelled") % {'school': visit.school}
        self.fields['body'].initial = _(
            "The workshop for %(school)s on %(visittime)s has been cancelled, sorry for any inconvenience.") % {
                                          'school': visit.school, 'visittime': visit.visit_time}


class DeleteForm(forms.Form):
    def __init__(self, *args, **kwargs):
        user = kwargs['user']
        del kwargs['user']
        school = kwargs['school']
        del kwargs['school']
        super(DeleteForm, self).__init__(*args, **kwargs)


# Custom field for school name
class SchoolNameField(forms.CharField):
    def __init__(self, *args, **kwargs):
        self.chapter = None
        self.school_id = None
        super(SchoolNameField, self).__init__(*args, **kwargs)

    # This function checks for the uniqueness of the school name within the chapter.
    # School names may not necessarily be unique globally across all chapters, thus
    # one cannot simply use the built-in Django functionality to specify this field
    # as a unique field.
    def clean(self, value):
        if value == '':
            if self.required:
                raise forms.ValidationError(_('This field is required.'))
            else:
                return ''
        if School.objects.filter(Q(chapter=self.chapter), ~Q(pk=self.school_id), Q(name=value)).count() > 0:
            raise forms.ValidationError(_('There is already a school with that name.'))
        else:
            return value


# Form to add or edit a school
class SchoolFormPartOne(forms.Form):
    def __init__(self, *args, **kwargs):
        chapter = kwargs['chapter']
        del kwargs['chapter']
        school_id = kwargs['school_id']
        del kwargs['school_id']
        super(SchoolFormPartOne, self).__init__(*args, **kwargs)
        self.fields['name'].chapter = chapter
        self.fields['name'].school_id = school_id
        self.fields['address_state'].initial = chapter.state
        if chapter.country:
            self.fields['address_country'].initial = chapter.country.pk
        else:
            self.fields['address_country'].initial = 'AU'

    name = SchoolNameField(max_length=128, label=_("Name"), required=True, widget=forms.TextInput(attrs={'size': '30'}))
    address_street = forms.CharField(label=_("Street"), required=False, widget=forms.TextInput(attrs={'size': '30'}))
    address_city = forms.CharField(label=_("City"), required=False, widget=forms.TextInput(attrs={'size': '30'}))
    address_state = forms.CharField(label=_("State"), required=True, widget=forms.TextInput(attrs={'size': '30'}),
                                    help_text="Use the abbreviation, e.g. 'VIC' not 'Victoria'")
    address_postcode = forms.CharField(label=_("Postcode"), required=False,
                                       widget=forms.TextInput(attrs={'size': '30'}))
    address_country = forms.ModelChoiceField(label=_("Country"), queryset=Country.objects.all(), initial='AU')


class SchoolFormPartTwo(forms.Form):
    contact_person = forms.CharField(max_length=128, label=_("Name"), required=False,
                                     widget=forms.TextInput(attrs={'size': '30'}))
    contact_position = forms.CharField(max_length=128, label=_("Position"), required=False,
                                       widget=forms.TextInput(attrs={'size': '30'}))
    contact_email = forms.CharField(max_length=128, label=_("Email"), required=False,
                                    widget=forms.TextInput(attrs={'size': '30'}))
    contact_phone = forms.CharField(max_length=128, label=_("Phone"), required=False,
                                    widget=forms.TextInput(attrs={'size': '30'}))


class SchoolFormPartThree(forms.Form):
    notes = forms.CharField(label=_("Notes"), required=False, widget=forms.Textarea(attrs={'cols': '35', 'rows': '7'}))


class RSVPForm(forms.Form):
    leave_message = forms.BooleanField(required=False)
    message = forms.CharField(widget=TinyMCE(attrs={'cols': 60}), required=False)

    def __init__(self, *args, **kwargs):
        user = kwargs['user']
        del kwargs['user']
        visit = kwargs['event']
        del kwargs['event']
        super(RSVPForm, self).__init__(*args, **kwargs)


class StatsModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return obj.last_name + ", " + obj.first_name


# Form for entering workshop stats
class SchoolVisitStatsFormBase(forms.Form):
    visit_type = forms.ChoiceField(choices=VISIT_TYPES_BASE, required=False, help_text=_(
        'For an explanation of each type please see <a href="%s" target="_blank">here</a> (opens in new window)') % '/teaching/statshelp/')
    primary_girls_first = forms.IntegerField(required=False, min_value=0, widget=forms.TextInput(attrs={'size': '8'}))
    primary_girls_repeat = forms.IntegerField(required=False, min_value=0, widget=forms.TextInput(attrs={'size': '8'}))
    primary_boys_first = forms.IntegerField(required=False, min_value=0, widget=forms.TextInput(attrs={'size': '8'}))
    primary_boys_repeat = forms.IntegerField(required=False, min_value=0, widget=forms.TextInput(attrs={'size': '8'}))
    high_girls_first = forms.IntegerField(required=False, min_value=0, widget=forms.TextInput(attrs={'size': '8'}))
    high_girls_repeat = forms.IntegerField(required=False, min_value=0, widget=forms.TextInput(attrs={'size': '8'}))
    high_boys_first = forms.IntegerField(required=False, min_value=0, widget=forms.TextInput(attrs={'size': '8'}))
    high_boys_repeat = forms.IntegerField(required=False, min_value=0, widget=forms.TextInput(attrs={'size': '8'}))
    other_girls_first = forms.IntegerField(required=False, min_value=0, widget=forms.TextInput(attrs={'size': '8'}))
    other_girls_repeat = forms.IntegerField(required=False, min_value=0, widget=forms.TextInput(attrs={'size': '8'}))
    other_boys_first = forms.IntegerField(required=False, min_value=0, widget=forms.TextInput(attrs={'size': '8'}))
    other_boys_repeat = forms.IntegerField(required=False, min_value=0, widget=forms.TextInput(attrs={'size': '8'}))
    attended = StatsModelMultipleChoiceField(queryset=User.objects.none(),
                                             widget=FilteredSelectMultiple(_("Invitees"), False, attrs={'rows': 8}),
                                             required=False)
    notes = forms.CharField(label=_("General notes"), required=False,
                            widget=forms.Textarea(attrs={'cols': '35', 'rows': '7'}))

    def clean(self):
        cleaned_data = self.cleaned_data
        return cleaned_data


class SchoolVisitStatsForm(SchoolVisitStatsFormBase):
    # Override constructor to show only this chapter's users in the list to select who attended,
    # and by default select those users who had RSVP'd as attending.
    def __init__(self, *args, **kwargs):
        visit = kwargs['visit']
        del kwargs['visit']
        super(SchoolVisitStatsForm, self).__init__(*args, **kwargs)

        attending = EventAttendee.objects.filter(rsvp_status=2, event__id=visit.id).values_list('user_id')
        self.fields['attended'].queryset = User.objects.filter(is_active=True, chapter=visit.chapter).order_by(
            'last_name')
        self.fields['attended'].initial = [u.pk for u in User.objects.filter(id__in=attending)]
        self.fields['visit_type'].initial = ''
        self.fields['primary_girls_first'].initial = visit.numstudents


class SchoolVisitStatsFormInstant(SchoolVisitStatsFormBase):
    def __init__(self, *args, **kwargs):
        chapter = kwargs.pop('chapter')
        super(SchoolVisitStatsFormInstant, self).__init__(*args, **kwargs)

        if chapter is None:
            self.fields['attended'].queryset = User.objects.filter(is_active=True).order_by('last_name')
        else:
            self.fields['attended'].queryset = User.objects.filter(is_active=True, chapter=chapter).order_by(
                'last_name')

        self.fields['visit_type'].initial = ''


class ReportSelectorForm(forms.Form):
    start_date = forms.DateField(label='Report start date',
                                 widget=SelectDateWidget(years=range(20011, datetime.date.today().year + 1)),
                                 initial=datetime.date.today())
    end_date = forms.DateField(label='Report end date',
                               widget=SelectDateWidget(years=range(2011, datetime.date.today().year + 1)),
                               initial=datetime.date.today())
    visit_type = forms.ChoiceField(choices=VISIT_TYPES_REPORT, required=True, help_text=_(
        'For an explanation of each type please see <a href="%s" target="_blank">here</a> (opens in new window)') % '/teaching/statshelp/')
    printview = forms.BooleanField(label='Show printable version', required=False)
