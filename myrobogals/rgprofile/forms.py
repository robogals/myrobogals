import re
from datetime import datetime, date

from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth import authenticate
from django.db.models import Q
from django.forms.widgets import Widget, Select, TextInput, PasswordInput
from django.utils.dates import MONTHS
from django.utils.safestring import mark_safe
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import  PasswordResetForm as PassResetFrm

from myrobogals.rgchapter.models import DisplayColumn, ShirtSize
from myrobogals.rgmain.models import University, MobileRegex
from myrobogals.rgmain.utils import SelectDateWidget, email_re
from myrobogals.rgprofile.models import User
from myrobogals.settings import GENDERS


class EmailModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return obj.last_name + ", " + obj.first_name


class DPModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return obj.display_name_en


class EditListForm(forms.Form):
    name = forms.CharField(max_length=256)
    users = EmailModelMultipleChoiceField(queryset=User.objects.none(),
                                          widget=FilteredSelectMultiple(_("Members"), False, attrs={'rows': 20}),
                                          required=True)
    display_columns = DPModelMultipleChoiceField(queryset=DisplayColumn.objects.all().order_by('display_name_en'),
                                                 label=_("Columns to display"),
                                                 widget=FilteredSelectMultiple(_("Columns"), False, attrs={'rows': 10}),
                                                 required=True, initial=(26, 4, 15))
    notes = forms.CharField(required=False, widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        user = kwargs['user']
        del kwargs['user']
        super(EditListForm, self).__init__(*args, **kwargs)
        if user.is_superuser:
            self.fields['users'].queryset = User.objects.filter(is_active=True).order_by('last_name')
        else:
            self.fields['users'].queryset = User.objects.filter(chapter=user.chapter, is_active=True).order_by(
                'last_name')


class EditStatusForm(forms.Form):
    status = forms.CharField()
    users = EmailModelMultipleChoiceField(queryset=User.objects.none(),
                                          widget=FilteredSelectMultiple(_("Members"), False, attrs={'rows': 20}),
                                          required=True)

    def __init__(self, *args, **kwargs):
        user = kwargs['user']
        del kwargs['user']
        super(EditStatusForm, self).__init__(*args, **kwargs)
        if user.is_superuser:
            self.fields['users'].queryset = User.objects.filter(is_active=True).order_by('last_name')
        else:
            self.fields['users'].queryset = User.objects.filter(chapter=user.chapter, is_active=True).order_by(
                'last_name')


# Widget that shows a month and year field only
RE_DATE = re.compile(r'(\d{4})-(\d\d?)-(\d\d?)$')


class SelectMonthYearWidget(Widget):
    none_value = ('0', '---')
    month_field = '%s_month'
    year_field = '%s_year'

    def __init__(self, attrs=None, years=None, required=True):
        # years is an optional list/tuple of years to use in the "year" select box.
        self.attrs = attrs or {}
        self.required = required
        if years:
            self.years = years
        else:
            this_year = date.today().year
            self.years = range(this_year - 10, this_year + 10)

    def render(self, name, value, attrs=None):
        try:
            year_val, month_val = value.year, value.month
        except AttributeError:
            year_val = month_val = None
            if isinstance(value, basestring):
                match = RE_DATE.match(value)
                if match:
                    year_val, month_val, day_val = [int(v) for v in match.groups()]

        output = []

        if 'id' in self.attrs:
            id_ = self.attrs['id']
        else:
            id_ = 'id_%s' % name

        local_attrs = self.build_attrs(id=self.month_field % id_)
        month_choices = MONTHS.items()
        month_choices.insert(0, self.none_value)
        # month_choices.sort()
        s = Select(choices=month_choices)
        select_html = s.render(self.month_field % name, month_val, local_attrs)
        output.append(select_html)

        year_choices = [(i, i) for i in self.years]
        year_choices.insert(0, self.none_value)
        local_attrs['id'] = self.year_field % id_
        s = Select(choices=year_choices)
        select_html = s.render(self.year_field % name, year_val, local_attrs)
        output.append(select_html)

        return mark_safe(u'\n'.join(output))

    def id_for_label(self, id_):
        return '%s_month' % id_

    id_for_label = classmethod(id_for_label)

    def value_from_datadict(self, data, files, name):
        y = data.get(self.year_field % name)
        m = data.get(self.month_field % name)
        d = "01"
        if y == m == "0":
            return None
        if y and m:
            return '%s-%s-%s' % (y, m, d)
        return data.get(name, None)


class MobileTextInput(TextInput):
    def render(self, name, value, attrs=None):
        if value != None:
            if value[0:1] in ('1', '2', '3', '4', '5', '6', '7', '8', '9'):
                value = '+' + value
        return super(MobileTextInput, self).render(name, value, attrs)


# Custom mobile field
class MobileField(forms.CharField):
    chapter = None

    def __init__(self, *args, **kwargs):
        self.chapter = kwargs['chapter']
        del kwargs['chapter']
        super(MobileField, self).__init__(*args, **kwargs)

    # This function:
    #    - validates the number
    #    - strips leading digits
    #    - prepends the country code if needed
    def clean(self, value):
        num = value.strip().replace(' ', '').replace('+', '')
        if num == '':
            return ''
        regexes = MobileRegex.objects.filter(collection=self.chapter.mobile_regexes)
        try:
            for regex in regexes:
                matches = re.compile(regex.regex).findall(num)
                if matches == []:
                    continue
                else:
                    num = num[regex.strip_digits:]
                    return regex.prepend_digits + num
            # If we got this far, then it didn't match any of the regexes
            raise forms.ValidationError(self.chapter.mobile_regexes.errmsg)
        except ValueError:
            raise forms.ValidationError(self.chapter.mobile_regexes.errmsg)


# Custom student number field
class StudentNumField(forms.CharField):
    def __init__(self, *args, **kwargs):
        self.chapter = None
        self.user_id = None
        super(StudentNumField, self).__init__(*args, **kwargs)

    # This function checks for the uniqueness of the student number within the chapter.
    # Student numbers may not necessarily be unique globally across all universities,
    # thus one cannot simply use the built-in Django functionality to specify this field
    # as a unique field.
    def clean(self, value):
        if value == '':
            if self.required:
                raise forms.ValidationError(_('This field is required.'))
            else:
                return ''

        u_id = None if self.user_id == '' else self.user_id

        if User.objects.filter(Q(chapter=self.chapter), ~Q(pk=u_id), Q(student_number=value)).count() > 0:
            raise forms.ValidationError(_('There is already a member with that student number. Click "forgot password" to the left to recover your existing account, if necessary.'))
        else:
            return value


# Custom t-shirt size selection field
class ShirtChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.size_long


# Personal information
class FormPartOne(forms.Form):
    def __init__(self, *args, **kwargs):
        chapter = kwargs['chapter']
        del kwargs['chapter']
        user_id = kwargs['user_id']
        del kwargs['user_id']
        super(FormPartOne, self).__init__(*args, **kwargs)
        self.fields['mobile'] = MobileField(label=_('Mobile phone'), max_length=20, required=False,
                                            widget=MobileTextInput(), chapter=chapter)

        if chapter.student_number_enable:
            self.fields['student_number'].label = chapter.student_number_label
            self.fields['student_number'].required = chapter.student_number_required
            self.fields['student_number'].chapter = chapter
            self.fields['student_number'].user_id = user_id
        else:
            del self.fields['student_number']

        if chapter.student_union_enable:
            self.fields['union_member'].label = chapter.student_union_label
            self.fields['union_member'].required = chapter.student_union_required
        else:
            del self.fields['union_member']

        if chapter.tshirt_enable:
            self.fields['tshirt'].label = chapter.tshirt_label
            self.fields['tshirt'].required = chapter.tshirt_required
            self.fields['tshirt'].queryset = ShirtSize.objects.filter(chapter=chapter)
        else:
            del self.fields['tshirt']

        if chapter.police_check_number_enable:
            self.fields['police_check_number'].label = chapter.police_check_number_label
            self.fields['police_check_expiration'].label = 'Expiration Date'
            self.fields['police_check_number'].required = chapter.police_check_number_required
            self.fields['police_check_expiration'].required = chapter.police_check_number_required
        else:
            del self.fields['police_check_number']
            del self.fields['police_check_expiration']

    username = forms.CharField(label=_('Username'), max_length=30)
    first_name = forms.CharField(label=_('First name'), max_length=30)
    last_name = forms.CharField(label=_('Last name'), max_length=30)
    email = forms.EmailField(label=_('Email'), max_length=64)
    student_number = StudentNumField(max_length=32)
    union_member = forms.BooleanField()
    tshirt = ShirtChoiceField(queryset=ShirtSize.objects.none())
    alt_email = forms.EmailField(label=_('Alternate email'), max_length=64, required=False)
    mobile = forms.BooleanField()
    gender = forms.ChoiceField(label=_('Gender'), choices=GENDERS)
    police_check_number = forms.CharField(help_text=_(
        "Also known as the number that allows you to volunteer with Robogals. Ask an executive member if unsure. When this number is entered, your chapter's executive members will be notified"))
    police_check_expiration = forms.DateField(widget=SelectDateWidget(), help_text=_(
        "You must also enter an expiration date shown on your card. myRobogals will inform you and your chapter executives when the card is about to expire"))

    def clean(self):
        cleaned_data = super(FormPartOne, self).clean()
        police_check_number = cleaned_data.get("police_check_number")
        police_check_expiration = cleaned_data.get("police_check_expiration")

        if police_check_number and police_check_expiration:
            # Only check expiration date if field is required and the user has entered a p/c number
            if self.fields['police_check_expiration'].required or police_check_number != '':
                local_time = datetime.date(now())

                # Check if card has expired in their local time only if they've made changes
                if police_check_expiration < local_time:
                    self.add_error('police_check_expiration', 'The card you have entered has already expired')
            else:
                cleaned_data["police_check_expiration"] = None

        return cleaned_data


# Privacy settings
class FormPartTwo(forms.Form):
    def __init__(self, *args, **kwargs):
        chapter = kwargs['chapter']
        del kwargs['chapter']
        super(FormPartTwo, self).__init__(*args, **kwargs)

    PRIVACY_CHOICES = (
        (20, _('Everyone (the whole internet)')),
        (10, _('Only Robogals members')),
        (5, _('Only Robogals members in my chapter')),
        (0, _('Only committee')),
    )

    privacy = forms.ChoiceField(label=_('Who can see my profile?'), choices=PRIVACY_CHOICES, initial=5)
    dob_public = forms.BooleanField(label=_('Show date of birth in my profile'), required=False)
    email_public = forms.BooleanField(label=_('Show email address in my profile'), required=False)


# Profile information
class FormPartThree(forms.Form):
    def __init__(self, *args, **kwargs):
        chapter = kwargs['chapter']
        del kwargs['chapter']
        super(FormPartThree, self).__init__(*args, **kwargs)

    COURSE_TYPE_CHOICES = (
        (0, '---'),
        (1, _('Undergraduate')),
        (2, _('Postgraduate'))
    )

    STUDENT_TYPE_CHOICES = (
        (0, '---'),
        (1, _('Local')),
        (2, _('International'))
    )

    dob = forms.DateField(label=_('Date of birth'), widget=SelectDateWidget(), required=False)
    course = forms.CharField(label=_('Course'), max_length=128, required=False)
    uni_start = forms.DateField(label=_('Started university'), widget=SelectMonthYearWidget(), required=False)
    uni_end = forms.DateField(label=_('Will finish university'), widget=SelectMonthYearWidget(), required=False)
    university = forms.ModelChoiceField(label=_('University'), queryset=University.objects.all(), required=False)
    course_type = forms.ChoiceField(label=_('Course level'), choices=COURSE_TYPE_CHOICES, required=False)
    student_type = forms.ChoiceField(label=_('Student type'), choices=STUDENT_TYPE_CHOICES, required=False)
    job_title = forms.CharField(label=_('Occupation'), max_length=128, required=False)
    company = forms.CharField(label=_('Employer'), max_length=128, required=False)
    bio = forms.CharField(label=_('About me (for profile page)'), required=False,
                          widget=forms.Textarea(attrs={'cols': '35', 'rows': '7'}))
# job_title = forms.CharField(_('Job title'), max_length=128, required=False)
# company = forms.CharField(_('Company'), max_length=128, required=False)


# User preferences
class FormPartFour(forms.Form):
    def __init__(self, *args, **kwargs):
        chapter = kwargs['chapter']
        del kwargs['chapter']
        super(FormPartFour, self).__init__(*args, **kwargs)
        self.fields['email_chapter_optin'].label = _('Allow %s to send me email updates') % chapter.name
        self.fields['mobile_marketing_optin'].label = _('Allow %s to send me SMS updates') % chapter.name
        if chapter.country.code == 'AU':
            self.fields['email_careers_newsletter_AU_optin'].initial = True
        else:
            self.fields['email_careers_newsletter_AU_optin'].initial = False

    email_reminder_optin = forms.BooleanField(label=_('Allow email reminders about my upcoming school visits'),
                                              initial=True, required=False)
    mobile_reminder_optin = forms.BooleanField(label=_('Allow SMS reminders about my upcoming school visits'),
                                               initial=True, required=False)
    email_chapter_optin = forms.BooleanField(initial=True, required=False)
    mobile_marketing_optin = forms.BooleanField(initial=True, required=False)
    email_newsletter_optin = forms.BooleanField(
        label=_('Subscribe to The Amplifier, the monthly email newsletter of Robogals Global'), initial=True,
        required=False)
    email_careers_newsletter_AU_optin = forms.BooleanField(
        label=_('Subscribe to Robogals Careers Newsletter - Australia'), required=False)


# Bio
class FormPartFive(forms.Form):
    def __init__(self, *args, **kwargs):
        chapter = kwargs['chapter']
        del kwargs['chapter']
        super(FormPartFive, self).__init__(*args, **kwargs)

    security_check = forms.BooleanField(label=_('Passed the Police Check'), initial=False, required=False)
    trained = forms.BooleanField(label=_('Trained and approved to teach'), initial=False, required=False)
    internal_notes = forms.CharField(label=_('Internal notes'), required=False,
                                     widget=forms.Textarea(attrs={'cols': '35', 'rows': '7'}))


class LoginForm(forms.Form):
    username = forms.CharField(max_length=255, required=True, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Username', 'id': 'inputError1'}))
    password = forms.CharField(widget=PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
                               required=True)

    user = None

    def clean(self):
        cleaned_data = super(LoginForm, self).clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        email_login = False
        # Check if they are using email to login
        if email_re.match(username):
            try:
                u = User.objects.get(email=username)
                username = u.username
                email_login = True
            except User.MultipleObjectsReturned:
                    self.add_error('username', 'That email address has multiple users associated with it. Please log in using your username.')
            except User.DoesNotExist:
                self.add_error('username', 'Invalid email address or password')

        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                self.user = user
            else:
                self.add_error('username', 'Your account has been disabled, please contact support')
        else:
            if email_login:
                self.add_error('username', 'Invalid email address or password')
            else:
                self.add_error('username', 'Invalid username or password')
class PasswordResetForm(PassResetFrm):
    email = forms.CharField(max_length=255, required=True, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Email', 'id': 'inputError1'}))

class CodeOfConductForm(forms.Form):
    code_of_conduct = forms.BooleanField(required=True)


class CSVUsersUploadForm(forms.Form):
    csvfile = forms.FileField()
    updateuser = forms.BooleanField(label=_('Update (instead of create) members if the username already exists'),
                                    required=False)
    ignore_email = forms.BooleanField(label=_('Ignore rows that have the same email address as an existing member'),
                                      initial=True, required=False)


class WelcomeEmailForm(forms.Form):
    def __init__(self, *args, **kwargs):
        chapter = kwargs['chapter']
        del kwargs['chapter']
        super(WelcomeEmailForm, self).__init__(*args, **kwargs)
        self.fields['subject'].initial = chapter.welcome_email_subject
        self.fields['body'].initial = chapter.welcome_email_msg
        self.fields['html'].initial = chapter.welcome_email_html

    importaction = forms.ChoiceField(
        choices=((1, _('Add members, and send welcome email')), (2, _('Add members, with no further action'))),
        initial=1)
    subject = forms.CharField(max_length=256, required=False)
    body = forms.CharField(widget=forms.Textarea, required=False)
    html = forms.BooleanField(required=False)


class DefaultsFormOne(forms.Form):
    COURSE_TYPE_CHOICES = (
        (0, '---'),
        (1, 'Undergraduate'),
        (2, 'Postgraduate')
    )

    STUDENT_TYPE_CHOICES = (
        (0, '---'),
        (1, 'Local'),
        (2, 'International')
    )

    date_joined = forms.DateField(label=_('Date joined'), widget=SelectDateWidget(), required=False)
    gender = forms.ChoiceField(choices=GENDERS, initial=0)
    uni_start = forms.DateField(label=_('Started university'), widget=SelectMonthYearWidget(), required=False)
    uni_end = forms.DateField(label=_('Will finish university'), widget=SelectMonthYearWidget(), required=False)
    university = forms.ModelChoiceField(queryset=University.objects.all(), required=False)
    course_type = forms.ChoiceField(label=_('Course level'), choices=COURSE_TYPE_CHOICES, required=False)
    student_type = forms.ChoiceField(label=_('Student type'), choices=STUDENT_TYPE_CHOICES, required=False)


class DefaultsFormTwo(forms.Form):
    email_reminder_optin = forms.BooleanField(label=_('Allow email reminders about upcoming school visits'),
                                              initial=True, required=False)
    mobile_reminder_optin = forms.BooleanField(label=_('Allow SMS reminders about upcoming school visits'),
                                               initial=True, required=False)
    email_chapter_optin = forms.BooleanField(label=_('Allow email updates from local Robogals chapter'), initial=True,
                                             required=False)
    mobile_marketing_optin = forms.BooleanField(label=_('Allow SMS updates from local Robogals chapter'), initial=True,
                                                required=False)
    email_newsletter_optin = forms.BooleanField(
        label=_('Subscribe to The Amplifier, the monthly email newsletter of Robogals Global'), initial=True,
        required=False)
    email_careers_newsletter_AU_optin = forms.BooleanField(
        label=_('Subscribe to Robogals Careers Newsletter - Australia'), required=False)


class WelcomeEmailFormTwo(forms.Form):
    def __init__(self, *args, **kwargs):
        chapter = kwargs['chapter']
        del kwargs['chapter']
        super(WelcomeEmailFormTwo, self).__init__(*args, **kwargs)
        self.fields['subject'].initial = chapter.welcome_email_subject
        self.fields['body'].initial = chapter.welcome_email_msg
        self.fields['html'].initial = chapter.welcome_email_html

    subject = forms.CharField(max_length=256)
    body = forms.CharField(widget=forms.Textarea)
    html = forms.BooleanField(required=False)
