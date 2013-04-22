import datetime
from datetime import date
import urllib
from myrobogals import auth
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.db.models.manager import EmptyManager
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import smart_str
from django.utils.hashcompat import md5_constructor, sha_constructor
from django.db.models.fields import PositiveIntegerField
from myrobogals.rgmain.models import University, Country, MobileRegexCollection
from myrobogals.rgprofile.files import get_profile_path
from myrobogals.rgchapter.models import DisplayColumn, ShirtSize
from myrobogals import rgprofile
from django.db import connection, transaction
from pytz import timezone, utc
import json, urllib, urllib2

UNUSABLE_PASSWORD = '!' # This will never be a valid hash

try:
    set
except NameError:
    from sets import Set as set   # Python 2.3 fallback

def get_hexdigest(algorithm, salt, raw_password):
    """
    Returns a string of the hexdigest of the given plaintext password and salt
    using the given algorithm ('md5', 'sha1' or 'crypt').
    """
    raw_password, salt = smart_str(raw_password), smart_str(salt)
    if algorithm == 'crypt':
        try:
            import crypt
        except ImportError:
            raise ValueError('"crypt" password algorithm not supported in this environment')
        return crypt.crypt(raw_password, salt)

    if algorithm == 'md5':
        return md5_constructor(salt + raw_password).hexdigest()
    elif algorithm == 'sha1':
        return sha_constructor(salt + raw_password).hexdigest()
    raise ValueError("Got unknown password algorithm type in password.")

def check_password(raw_password, enc_password):
    """
    Returns a boolean of whether the raw_password was correct. Handles
    encryption formats behind the scenes.
    """
    algo, salt, hsh = enc_password.split('$')
    return hsh == get_hexdigest(algo, salt, raw_password)

class SiteProfileNotAvailable(Exception):
    pass

class Permission(models.Model):
    """The permissions system provides a way to assign permissions to specific users and groups of users.

    The permission system is used by the Django admin site, but may also be useful in your own code. The Django admin site uses permissions as follows:

        - The "add" permission limits the user's ability to view the "add" form and add an object.
        - The "change" permission limits a user's ability to view the change list, view the "change" form and change an object.
        - The "delete" permission limits the ability to delete an object.

    Permissions are set globally per type of object, not per specific object instance. It is possible to say "Mary may change news stories," but it's not currently possible to say "Mary may change news stories, but only the ones she created herself" or "Mary may only change news stories that have a certain status or publication date."

    Three basic permissions -- add, change and delete -- are automatically created for each Django model.
    """
    name = models.CharField('name', max_length=50)
    content_type = models.ForeignKey(ContentType)
    codename = models.CharField('codename', max_length=100)

    class Meta:
        verbose_name = 'permission'
        verbose_name_plural = 'permissions'
        unique_together = (('content_type', 'codename'),)
        ordering = ('content_type__app_label', 'codename')

    def __unicode__(self):
        return u"%s | %s | %s" % (
            unicode(self.content_type.app_label),
            unicode(self.content_type),
            unicode(self.name))

class Timezone(models.Model):
	description = models.CharField(max_length=64)

	def __unicode__(self):
		return self.description

	def tz_obj(self):
		return timezone(self.description)

class EmailDomain(models.Model):
	domainname = models.CharField(max_length=64)

	def __unicode__(self):
		return self.domainname

	class Meta:
		ordering = ('domainname',)

NAME_DISPLAYS = (
    (0, 'First Last (e.g. English)'),
    (1, 'Last First (e.g. East Asian names in English characters)'),
    (2, 'LastFirst (e.g. East Asian names in characters)')
)

class Group(models.Model):
    """Groups are a generic way of categorizing users to apply permissions, or some other label, to those users. A user can belong to any number of groups.

    A user in a group automatically has all the permissions granted to that group. For example, if the group Site editors has the permission can_edit_home_page, any user in that group will have that permission.

    Beyond permissions, groups are a convenient way to categorize users to apply some label, or extended functionality, to them. For example, you could create a group 'Special users', and you could write code that would do special things to those users -- such as giving them access to a members-only portion of your site, or sending them members-only e-mail messages.
    """

    STATUS_CHOICES = (
        (0, 'Active'),
        (1, 'Inactive'),
        (2, 'Hidden'),
    )

    name = models.CharField('Name', max_length=80, unique=True)
    #permissions = models.ManyToManyField(Permission, blank=True)
    short = models.CharField('Short Name', max_length=80, help_text='Use city name in local language (e.g. Melbourne) unless this is a regional body (e.g. Asia Pacific)')
    short_en = models.CharField('English Short Name', max_length=80, help_text='Use city name in English (e.g. Melbourne) unless this is a regional body (e.g. Asia Pacific)')
    location = models.CharField('Location', help_text='Use the format: City, Country (e.g. Melbourne, Australia); in the US also include state (e.g. Pasadena, California, USA)', max_length=64, blank=True)
    myrobogals_url = models.CharField('myRobogals URL', max_length=16, unique=True, help_text="The chapter page will be https://my.robogals.org/chapters/&lt;url&gt;/ - our convention is to use lowercase city name in English")
    creation_date = models.DateField(help_text='Our convention is to use the first day of the SINE at which this chapter was founded')
    university = models.ForeignKey(University, null=True, blank=True)
    parent = models.ForeignKey('self', verbose_name='Parent', null=True, blank=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=2)
    address = models.TextField('Postal address', help_text="Don't put city, state and postcode above, there's a spot for them right below", blank=True)
    city = models.CharField('City/Suburb', max_length=64, blank=True)
    state = models.CharField('State/Province', max_length=16, help_text="Use the abbreviation, e.g. 'VIC' not 'Victoria'", blank=True)
    postcode = models.CharField('Postcode', max_length=16, blank=True)
    country = models.ForeignKey(Country, verbose_name="Country", default="AU", blank=True, null=True)
    timezone = models.ForeignKey(Timezone)
    faculty_contact = models.CharField('Name', max_length=64, blank=True, help_text="e.g. Professor John Doe")
    faculty_position = models.CharField('Position', max_length=64, blank=True, help_text="e.g. Associate Dean")
    faculty_department = models.CharField('Department', max_length=64, blank=True, help_text="e.g. Faculty of Engineering")
    faculty_email = models.CharField('Email', max_length=64, blank=True)
    faculty_phone = models.CharField('Phone', max_length=32, blank=True, help_text="International format, e.g. +61 3 8344 4000")
    website_url = models.CharField('Website URL', max_length=128, blank=True)
    facebook_url = models.CharField('Facebook URL', max_length=128, blank=True)
    is_joinable = models.BooleanField('Joinable', default=True, help_text='People can join this chapter through the website. Untick this box for regional bodies, e.g. Robogals Asia Pacific.')
    infobox = models.TextField(blank=True)
    photo = models.FileField(upload_to='unipics', blank=True, help_text='This must be scaled down before uploading. It should be exactly 320px wide, and while the height can vary, it should be oriented landscape.')
    emailtext = models.TextField('Default email reminder text', blank=True)
    smstext = models.TextField('Default SMS reminder text', blank=True)
    default_email_domain = models.ManyToManyField(EmailDomain, verbose_name="Allowed email domains")
    upload_exec_list = models.BooleanField('Enable daily FTP upload of executive committee list', default=False)
    ftp_host = models.CharField('FTP host', max_length=64, blank=True)
    ftp_user = models.CharField('FTP username', max_length=64, blank=True)
    ftp_pass = models.CharField('FTP password', max_length=64, blank=True)
    ftp_path = models.CharField('FTP path', max_length=64, blank=True, help_text='Including directory and filename, e.g. web/content/team.html')
    mobile_regexes = models.ForeignKey(MobileRegexCollection)
    student_number_enable = models.BooleanField('Enable student number field')
    student_number_required = models.BooleanField('Require student number field')
    student_number_label = models.CharField('Label for student number field', max_length=64, blank=True)
    student_union_enable = models.BooleanField('Enable student union member checkbox')
    student_union_required = models.BooleanField('Require student union member checkbox')
    student_union_label = models.CharField('Label for student union member checkbox', max_length=64, blank=True)
    welcome_email_enable = models.BooleanField('Enable welcome email for new signups', default=True)
    welcome_email_subject = models.CharField('Subject', max_length=128, blank=True, default='Welcome to Robogals!')
    welcome_email_msg = models.TextField('Message', blank=True, default="Dear {user.first_name},\n\nThankyou for joining {chapter.name}!\n\nYour username and password for myRobogals can be found below:\n\nUsername: {user.username}\nPassword: {plaintext_password}\nLogin at https://my.robogals.org\n\nRegards,\n\n{chapter.name}\n")
    welcome_email_html = models.BooleanField('HTML')
    invite_email_subject = models.CharField('Subject', max_length=128, blank=True, default="Upcoming Robogals workshop")
    invite_email_msg = models.TextField('Message', blank=True, default="Hello,\n\n{user.chapter.name} will be conducting a workshop soon:\nWhen: {visit.visit_start.year}-{visit.visit_start.month}-{visit.visit_start.day}, {visit.visit_start.hour}:{visit.visit_start.minute} to {visit.visit_end.hour}:{visit.visit_end.minute}\nLocation: {visit.location}\nSchool: {visit.school.name}\n\nTo accept or decline this invitation to volunteer at this workshop, please visit https://my.robogals.org/teaching/{visit.pk}/\n\nThanks,\n\n{user.first_name}")
    invite_email_html = models.BooleanField('HTML', default=False)
    welcome_page = models.TextField('Welcome page HTML', blank=True, default="Congratulations on becoming a member of {chapter.name}, and welcome to the international network of Robogals members - students around the world committed to increasing female participation in engineering!<br>\n<br>\nYour member account has been created - simply log in using the form to the left.")
    join_page = models.TextField('Join page HTML', blank=True, help_text='This page is shown if the chapter is not joinable via myRobogals. It should explain how to join this chapter, e.g. who to contact.')
    notify_enable = models.BooleanField('Notify when a new member signs up online')
    notify_list = models.ForeignKey('rgprofile.UserList', verbose_name='Who to notify', blank=True, null=True)
    sms_limit = models.IntegerField('Monthly SMS limit', default=1000)
    display_columns = models.ManyToManyField(DisplayColumn, help_text='Default values: get_full_name, email, mobile.')
    tshirt_enable = models.BooleanField('Enable T-shirt drop-down')
    tshirt_required = models.BooleanField('Require T-shirt drop-down')
    tshirt_label = models.CharField('Label for T-shirt drop-down', max_length=64, blank=True)
    name_display = models.IntegerField("Name display", choices=NAME_DISPLAYS, default=0)
    goal = models.IntegerField("Goal", default=0, blank=True, null=True)
    goal_start = models.DateField("Goal start date", blank=True, null=True, help_text='Our convention is to use the first day of the SINE at which they set their current-year goal')
    exclude_in_reports = models.BooleanField('Exclude this chapter in global reports')
    latitude = models.FloatField(blank=True, null=True, help_text='If blank, will be automatically filled in by Google Maps API when this chapter is made active. Value can be entered here manually if necessary.')
    longitude = models.FloatField(blank=True, null=True, help_text='If blank, will be automatically filled in by Google Maps API when this chapter is made active. Value can be entered here manually if necessary.')

    class Meta:
        verbose_name = 'chapter'
        verbose_name_plural = 'chapters'

    def __unicode__(self):
        return self.name
    
    # N.B. this function only works with three levels or less
    def do_membercount(self, type):
        cursor = connection.cursor()
        cursor.execute('SELECT id FROM auth_group WHERE parent_id = ' + str(self.pk))
        ids_csv = ''
        while (1):
            ids = cursor.fetchone()
            if ids:
                ids_csv = ids_csv + ', ' + str(ids[0])
            else:
                break
        if ids_csv:
            cursor.execute('SELECT id FROM auth_group WHERE parent_id IN (0' + ids_csv + ')')
            while (1):
                ids = cursor.fetchone()
                if ids:
                    ids_csv = ids_csv + ', ' + str(ids[0])
                else:
                    break
        if type == 0:
            cursor.execute('SELECT COUNT(id) FROM auth_user WHERE is_active = 1 AND chapter_id IN (' + str(self.pk) + ids_csv + ')')
        else:
            cursor.execute('SELECT COUNT(u.id) FROM auth_user AS u, auth_memberstatus AS ms WHERE u.is_active = 1 AND u.chapter_id IN (' + str(self.pk) + ids_csv + ') AND u.id = ms.user_id AND ms.statusType_id = ' + str(type) + ' AND ms.status_date_end IS NULL')
        count = cursor.fetchone()
        if count:
            return int(count[0])
        else:
            return 0

    def membercount(self):
    	return self.do_membercount(0)

    def membercount_student(self):
    	return self.do_membercount(1)

    def local_time(self):
    	return datetime.datetime.utcnow().replace(tzinfo=utc).astimezone(self.timezone.tz_obj())
    
    def get_absolute_url(self):
    	return "/chapters/%s/" % self.myrobogals_url

    def save(self, *args, **kwargs):
        if (self.status == 0) and (self.university != None) and ((self.latitude == None) or (self.longitude == None)):
            try:
                data = {}
                data['address'] = self.university.name + ', ' + self.location
                data['sensor'] = 'false'
                url_values = urllib.urlencode(data)
                url = 'http://maps.googleapis.com/maps/api/geocode/json'
                full_url = url + '?' + url_values
                data = urllib2.urlopen(full_url, timeout=2)
                result = json.loads(data.read())
                if result['status'] == 'OK':
                    self.latitude = result['results'][0]['geometry']['location']['lat']
                    self.longitude = result['results'][0]['geometry']['location']['lng']
            except:
            	pass
        super(Group, self).save(*args, **kwargs)

class UserManager(models.Manager):
    def create_user(self, username, email, password=None):
        "Creates and saves a User with the given username, e-mail and password."
        now = datetime.datetime.now()
        user = self.model(None, username, '', '', email.strip().lower(), '', 'placeholder', False, True, False, now, now)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user

    def create_superuser(self, username, email, password):
        u = self.create_user(username, email, password)
        u.is_staff = True
        u.is_active = True
        u.is_superuser = True
        u.save()
        return u

    def make_random_password(self, length=10, allowed_chars='abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789'):
        "Generates a random password with the given length and given allowed_chars"
        # Note that default value of allowed_chars does not have "I" or letters
        # that look like it -- just to avoid confusion.
        from random import choice
        return ''.join([choice(allowed_chars) for i in range(length)])

class PositiveBigIntegerField(PositiveIntegerField):
	empty_strings_allowed = False
	
	def get_internal_type(self):
		return "PositiveBigIntegerField"
	
	def db_type(self, connection):
		return "bigint UNSIGNED"

class MemberStatusType(models.Model):
	PERSONTYPES = (
		(0, 'N/A'),
		(1, 'Student'),
		(2, 'Employed'),
	)
	description = models.CharField(max_length=64)
	chapter = models.ForeignKey(Group, null=True, blank=True)
	type_of_person = models.IntegerField(choices=PERSONTYPES, default=0)
	
	def idstr(self):
		return str(self.id)

	def __unicode__(self):
		return self.description
	
	class Meta:
		verbose_name = "member status"
		verbose_name_plural = "member statuses"

class MemberStatus(models.Model):
	user = models.ForeignKey('User')
	statusType = models.ForeignKey(MemberStatusType)
	status_date_start = models.DateField(default=date.today, null=True, blank=True)
	status_date_end = models.DateField(null=True, blank=True)

	def __unicode__(self):
		if (self.status_date_end):
			return self.statusType.description + " (" + self.status_date_start.strftime("%b %Y") + " - " + self.status_date_end.strftime("%b %Y") + ")"
		else:
			return self.statusType.description + " (" + self.status_date_start.strftime("%b %Y") + " - present)"

	class Meta:
		ordering = ('-status_date_end', '-status_date_start')

class User(models.Model):
    GENDERS = (
    	(0, 'No answer'),
    	(1, 'Male'),
    	(2, 'Female'),
    )
    
    PRIVACY_CHOICES = (
    	(20, 'Public'),
    	(10, 'Only Robogals members can see'),
    	(5, 'Only Robogals members in my chapter can see'),
    	(0, 'Private (only committee can see)'),
    )
    
    COURSE_TYPE_CHOICES = (
    	(0, 'No answer'),
    	(1, 'Undergraduate'),
    	(2, 'Postgraduate'),
    )

    STUDENT_TYPE_CHOICES = (
    	(0, 'No answer'),
    	(1, 'Local'),
    	(2, 'International'),
    )

    username = models.CharField('Username', max_length=30, unique=True, help_text="Required. 30 characters or fewer. Alphanumeric characters only (letters, digits and underscores).")
    first_name = models.CharField('First name', max_length=30, blank=True)
    last_name = models.CharField('Last name', max_length=30, blank=True)
    email = models.EmailField('E-mail address', blank=True)
    new_email = models.EmailField('New e-mail address', blank=True)
    password = models.CharField('Password', max_length=128, help_text="Use '[algo]$[salt]$[hexdigest]' or use the <a href=\"password/\">change password form</a>.")
    is_staff = models.BooleanField('Exec access', default=False, help_text="Designates whether the user can use exec functions on the site. Note that this option is completely independent of positions defined below.")
    is_active = models.BooleanField('Active', default=True, help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.")
    is_superuser = models.BooleanField('Superuser access', default=False, help_text="Designates that this user is able to access superuser functions on the site, and ALL functions in the Global Admin Panel.")
    last_login = models.DateTimeField('Last login', default=datetime.datetime.now)
    date_joined = models.DateTimeField('Date joined', default=datetime.datetime.now)
    chapter = models.ForeignKey(Group, related_name='rgchapter', default=1)
    user_permissions = models.ManyToManyField(Permission, verbose_name='Django user permissions', blank=True, help_text="Allow access to individual functions in the Global Admin Panel. The user must have exec access for this to work. Don't change this unless you really know what you're doing!")
    alt_email = models.EmailField('Alternate e-mail address', blank=True)
    dob = models.DateField(null=True, blank=True)
    dob_public = models.BooleanField("Display date of birth in profile", default=False)
    email_public = models.BooleanField("Display email address in profile", default=False)
    course = models.CharField('Course', max_length=64, blank=True)
    uni_start = models.DateField(null=True, blank=True)
    uni_end = models.DateField(null=True, blank=True)
    university = models.ForeignKey(University, null=True, blank=True)
    job_title = models.CharField('Job title', max_length=128, blank=True)
    company = models.CharField('Company', max_length=128, blank=True)
    mobile = models.CharField('Mobile', max_length=16, blank=True)
    mobile_verified = models.BooleanField(default=False)
    email_reminder_optin = models.BooleanField("Allow email reminders", default=True)
    email_chapter_optin = models.BooleanField("Allow emails from chapter", default=True)
    mobile_reminder_optin = models.BooleanField("Allow mobile reminders", default=True)
    mobile_marketing_optin = models.BooleanField("Allow mobile marketing", default=False)
    email_newsletter_optin = models.BooleanField("Subscribe to The Amplifier", default=True)
    email_othernewsletter_optin = models.BooleanField("Subscribe to alumni newsletter (if alumni)", default=True, help_text="Ignored unless this user is actually alumni.  It is recommended that you leave this ticked so that the user will automatically be subscribed upon becoming alumni.")
    timezone = models.ForeignKey(Timezone, verbose_name="Override chapter's timezone", blank=True, null=True)
    photo = models.FileField(upload_to='profilepics', blank=True)
    bio = models.TextField(blank=True)
    internal_notes = models.TextField(blank=True)
    website = models.CharField("Personal website", max_length=200, blank=True)
    gender = models.IntegerField("Gender", choices=GENDERS, default=0)
    privacy = models.IntegerField("Profile privacy", choices=PRIVACY_CHOICES, default=5)
    course_type = models.IntegerField("Course level", choices=COURSE_TYPE_CHOICES, default=0)
    student_type = models.IntegerField("Student type", choices=STUDENT_TYPE_CHOICES, default=0)
    student_number = models.CharField('Student number', max_length=32, blank=True)
    union_member = models.BooleanField(default=False)
    tshirt = models.ForeignKey(ShirtSize, null=True, blank=True)
    trained = models.BooleanField(default=False)
    name_display = models.IntegerField("Override chapter's name display", choices=NAME_DISPLAYS, blank=True, null=True)
    forum_last_act = models.DateTimeField('Forum last activity', default=datetime.datetime.now)
    objects = UserManager()
    aliases = models.ManyToManyField('User', blank=True, null=True, related_name='user_aliases')
    email_careers_newsletter_AU_optin = models.BooleanField("Subscribe to The Careers Newsletter - AU", default=False)

    class Meta:
        verbose_name = 'member'
        ordering = ['username']

    def __unicode__(self):
        return self.username
    
    def age(self):
    	return int((date.today() - self.dob).days / 365.25)
    
    # This fixes members whose MemberStatus is broken.
    # It returns the new value.
    def fixmembertype(self):
    	# Get all types ever assigned to this member
    	ms_list = MemberStatus.objects.filter(user=self).order_by('status_date_end',)
    	n_total = len(ms_list)
    	if n_total == 0:
    		# This member never had a type
    		# Create the type "Student" effective from join date
    		student = MemberStatusType.objects.get(pk=1)
    		ms = MemberStatus(user=self, status_date_start=self.date_joined.date(), status_date_end=None, statusType=student)
    		ms.save()
    		return student
    	else:
    		# Get all types currently active on this member (should not be more than one)
    		ms_active_list = MemberStatus.objects.filter(user=self, status_date_end__isnull=True).order_by('status_date_start',)
    		n_active = len(ms_active_list)
    		if n_active > 1:
	    		# This member has more than one active type
    			# Deactivate all but the last type
    			for i in range(n_active-1):
    				ms = ms_active_list[i]
    				ms.status_date_end = datetime.datetime.now().date()
    				ms.save()
    			# Return the active status (i.e. last in the list)
    			return ms_active_list[n_active-1].statusType
    		elif n_active < 1:
    			# This member has old types but no current types
    			# Make the most recently ended type the current type
    			ms = ms_list[n_total-1]
    			ms.status_date_end = None
    			ms.save()
    			return ms.statusType
    		else:
    			# This user is not actually broken
    			# Return the actual current type
    			return ms_active_list[0].statusType

	# Return current member type
    def membertype(self):
    	try:
    		return MemberStatus.objects.get(user=self, status_date_end__isnull=True).statusType
    	except (MemberStatus.DoesNotExist, MemberStatus.MultipleObjectsReturned):
        	# The member type is broken, fix it and return the fixed value
    		return self.fixmembertype()

    # If they have set a timezone override, use that
    # otherwise use their chapter's timezone
    def tz_obj(self):
        if self.timezone:
            return self.timezone.tz_obj()
        else:
            return self.chapter.timezone.tz_obj()
    
    # Similar deal for name display
    def get_name_display(self):
        if self.name_display:
            return self.name_display
        else:
            return self.chapter.name_display

    def graduation_year(self):
        if self.uni_end:
            return self.uni_end.strftime("%Y")
        else:
            return ""

    def date_joined_local(self):
        return self.tz_obj().fromutc(self.date_joined)

    def get_absolute_url(self):
        return "/profile/%s/" % urllib.quote(smart_str(self.username))

    def is_anonymous(self):
        "Always returns False. This is a way of comparing User objects to anonymous users."
        return False

    def is_authenticated(self):
        """Always return True. This is a way to tell if the user has been authenticated in templates.
        """
        return True

    def get_full_name(self):
        if self.get_name_display() == 0:
	        full_name = u'%s %s' % (self.first_name, self.last_name)
	elif self.get_name_display() == 1:
	        full_name = u'%s %s' % (self.last_name, self.first_name)
	elif self.get_name_display() == 2:
	        full_name = u'%s%s' % (self.last_name, self.first_name)
        return full_name.strip()

    def has_cur_pos(self):
    	cursor = connection.cursor()
    	cursor.execute('SELECT COUNT(user_id) FROM `rgprofile_position` WHERE user_id = ' + str(self.pk) + ' AND position_date_end IS NULL')
    	ms = cursor.fetchone()
        if ms[0] > 0:
           return True
        else:
           return False

    def cur_positions(self):
        return rgprofile.models.Position.objects.filter(user=self, position_date_end__isnull=True)

    def has_robogals_email(self):
        try:
            domain = self.email.split('@', 1)[1]
            rgemail = EmailDomain.objects.filter(domainname=domain).count()
            if rgemail > 0:
                return True
            else:
                return False
        except IndexError:
            return False
            
    def set_password(self, raw_password):
        import random
        algo = 'sha1'
        salt = get_hexdigest(algo, str(random.random()), str(random.random()))[:5]
        hsh = get_hexdigest(algo, salt, raw_password)
        self.password = '%s$%s$%s' % (algo, salt, hsh)

    def check_password(self, raw_password):
        """
        Returns a boolean of whether the raw_password was correct. Handles
        encryption formats behind the scenes.
        """
        # Backwards-compatibility check. Older passwords won't include the
        # algorithm or salt.
        if '$' not in self.password:
            is_correct = (self.password == get_hexdigest('md5', '', raw_password))
            if is_correct:
                # Convert the password to the new, more secure format.
                self.set_password(raw_password)
                self.save()
            return is_correct
        return check_password(raw_password, self.password)

    def set_unusable_password(self):
        # Sets a value that will never be a valid hash
        self.password = UNUSABLE_PASSWORD

    def has_usable_password(self):
        return self.password != UNUSABLE_PASSWORD

    def get_group_permissions(self):
        """
        Returns a list of permission strings that this user has through
        his/her groups. This method queries all available auth backends.

        permissions = set()
        for backend in auth.get_backends():
            if hasattr(backend, "get_group_permissions"):
                permissions.update(backend.get_group_permissions(self))
        return permissions
        """
        return set()

    def get_all_permissions(self):
        permissions = set()
        for backend in auth.get_backends():
            if hasattr(backend, "get_all_permissions"):
                permissions.update(backend.get_all_permissions(self))
        return permissions

    def has_perm(self, perm):
        """
        Returns True if the user has the specified permission. This method
        queries all available auth backends, but returns immediately if any
        backend returns True. Thus, a user who has permission from a single
        auth backend is assumed to have permission in general.
        """
        # Inactive users have no permissions.
        if not self.is_active:
            return False

        # Superusers have all permissions.
        if self.is_superuser:
            return True

        # Otherwise we need to check the backends.
        for backend in auth.get_backends():
            if hasattr(backend, "has_perm"):
                if backend.has_perm(self, perm):
                    return True
        return False

    def has_perms(self, perm_list):
        """Returns True if the user has each of the specified permissions."""
        for perm in perm_list:
            if not self.has_perm(perm):
                return False
        return True

    def has_module_perms(self, app_label):
        """
        Returns True if the user has any permissions in the given app
        label. Uses pretty much the same logic as has_perm, above.
        """
        if not self.is_active:
            return False

        if self.is_superuser:
            return True

        for backend in auth.get_backends():
            if hasattr(backend, "has_module_perms"):
                if backend.has_module_perms(self, app_label):
                    return True
        return False

    def get_and_delete_messages(self):
        messages = []
        for m in self.message_set.all():
            messages.append(m.message)
            m.delete()
        return messages

    def email_user(self, subject, message, from_email=None):
        "Sends an e-mail to this User."
        from django.core.mail import send_mail
        send_mail(subject, message, from_email, [self.email])

    def get_profile(self):
        """
        Returns site-specific profile for this user. Raises
        SiteProfileNotAvailable if this site does not allow profiles.
        """
        if not hasattr(self, '_profile_cache'):
            from django.conf import settings
            if not getattr(settings, 'AUTH_PROFILE_MODULE', False):
                raise SiteProfileNotAvailable
            try:
                app_label, model_name = settings.AUTH_PROFILE_MODULE.split('.')
                model = models.get_model(app_label, model_name)
                self._profile_cache = model._default_manager.get(user__id__exact=self.id)
                self._profile_cache.user = self
            except (ImportError, ImproperlyConfigured):
                raise SiteProfileNotAvailable
        return self._profile_cache
    
    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.is_staff = True  # Being a superuser implies being staff too
        super(User, self).save(*args, **kwargs)

class Message(models.Model):
    """
    The message system is a lightweight way to queue messages for given
    users. A message is associated with a User instance (so it is only
    applicable for registered users). There's no concept of expiration or
    timestamps. Messages are created by the Django admin after successful
    actions. For example, "The poll Foo was created successfully." is a
    message.
    """
    user = models.ForeignKey(User)
    message = models.TextField('message')

    def __unicode__(self):
        return self.message

class AnonymousUser(object):
    id = None
    username = ''
    is_staff = False
    is_active = False
    is_superuser = False
    #_groups = EmptyManager()
    _user_permissions = EmptyManager()

    def __init__(self):
        pass

    def __unicode__(self):
        return 'AnonymousUser'

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __eq__(self, other):
        return isinstance(other, self.__class__)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return 1 # instances always return the same hash value

    def save(self):
        raise NotImplementedError

    def delete(self):
        raise NotImplementedError

    def set_password(self, raw_password):
        raise NotImplementedError

    def check_password(self, raw_password):
        raise NotImplementedError

    #def _get_groups(self):
    #    return self._groups
    #groups = property(_get_groups)

    def _get_user_permissions(self):
        return self._user_permissions
    user_permissions = property(_get_user_permissions)

    def has_perm(self, perm):
        return False

    def has_perms(self, perm_list):
        return False

    def has_module_perms(self, module):
        return False

    def get_and_delete_messages(self):
        return []

    def is_anonymous(self):
        return True

    def is_authenticated(self):
        return False
