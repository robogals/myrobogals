from __future__ import unicode_literals
from future.builtins import *
import six
from django.utils.encoding import python_2_unicode_compatible



from django.db import models
from django.core import validators
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.contrib.sessions.models import Session

from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from django.conf import settings

# Based upon:
# * https://docs.djangoproject.com/en/1.6/topics/auth/customizing/#substituting-a-custom-user-model
# * http://www.caktusgroup.com/blog/2013/08/07/migrating-custom-user-model-django/
# * https://github.com/jonathanchu/django-custom-user-example/blob/master/customuser/accounts/models.py
# * https://github.com/django/django/blob/master/django/contrib/auth/models.py

#@python_2_unicode_compatible
class RobogalsUserManager(BaseUserManager):
    def _create_user(self, username, primary_email, given_name, password, is_superuser, **extra_fields):
        primary_email = self.normalize_email(primary_email)
        
        if not primary_email:
            raise ValueError(_('Users must have a primary email address.'))
        if not given_name:
            raise ValueError(_('Users must have a given name.'))
        if not username:
            #username = primary_email   # Use email address?
            raise ValueError(_('Users must have a username.'))
        
        now = timezone.now()
        
        user = self.model(
            username=username,
            primary_email=primary_email,
            given_name=given_name.strip(),
            is_superuser=is_superuser,
            date_joined=now,
            **extra_fields
        )
        
        user.set_password(password) # If password = None => unusable password.
        user.save(using=self._db)
        return user
        
    def create_user(self, username, primary_email, given_name, password=None, **extra_fields):
        return self._create_user(username, primary_email, given_name, password, is_superuser=False, **extra_fields)

    def create_superuser(self, username, primary_email, given_name, password, **extra_fields):
        return self._create_user(username, primary_email, given_name, password, is_superuser=True, **extra_fields)

@python_2_unicode_compatible
class RobogalsUser(AbstractBaseUser, PermissionsMixin):
    def uuid_generator():
        from uuid import uuid4
        return str(uuid4().hex)
        
    ############################################################################
    # Identifiers
    ############################################################################
    # Usernames will have uniqueness enforced and is required.
    #
    # To get around anonymous registrations (e.g. newsletter subscriptions), we
    # will generate random usernames on the fly in the save handler.
    #
    # Usernames will not be accepting Unicode characters due to conflicts with
    # future implementation of the messaging system.
    
    id = models.CharField(max_length=32, primary_key=True, default=uuid_generator)
    
    username = models.CharField(_('username'),
                                max_length=63,
                                unique=True,
                                validators=[
                                    validators.RegexValidator(r'^[\w.-]+$', _('This value may contain only alphanumeric and ./_/- characters.'), 'invalid')
                                ],
                                help_text=_('Username of length 63 characters or fewer, consisting of alphanumeric characters and any of ./_/- is required.'))

    # As primary emails are the unique identifier, this is required and
    # uniqueness enforced
    primary_email = models.EmailField(_('primary email address'),
                                      max_length=255,
                                      unique=True,
                                      validators=[
                                        validators.EmailValidator(_('Enter a valid primary email address.'), 'invalid')
                                      ],
                                      help_text=_('Primary email address of length 255 characters or fewer is required.'))

    # ... however the secondary email isn't.
    secondary_email = models.EmailField(_('secondary email address'),
                                        max_length=255,
                                        blank=True,
                                        validators=[
                                            validators.EmailValidator(_('Enter a valid secondary email address.'), 'invalid')
                                        ],
                                        help_text=_('Secondary email address of length 255 characters or fewer is optional.'))

    
    ############################################################################
    # Personal information
    ############################################################################
    # In following internationalisation guidelines, name fields are now set for
    # family/given/preferred rather than first/last.
    #
    # http://www.w3.org/International/questions/qa-personal-names
    family_name = models.CharField(_('family name'),
                                   max_length=63,
                                   blank=True,
                                   validators=[
                                        validators.RegexValidator(r'^[\s\w"\'-]+$', _('Enter a valid Romanised family name.'), 'invalid')
                                   ],
                                   help_text=_('Family name of length 63 Latin characters or fewer is optional.'))
    given_name = models.CharField(_('given name'),
                                  max_length=63,
                                  validators=[
                                        validators.RegexValidator(r'^[\s\w"\'-]+$', _('Enter a valid Romanised given name.'), 'invalid')
                                  ],
                                  help_text=_('Given name of length 63 Latin characters or fewer is required.'))
    preferred_name = models.CharField(_('preferred name'),
                                      max_length=127,
                                      blank=True,
                                      help_text=_('Preferred name of length 127 characters or fewer is optional. This name will be displayed preferrentially for most elements of myRobogals and related services.'))

    dob = models.DateField(_('date of birth'),
                            blank=True,
                            null=True)
                                        
    # Genders have now altered in definition to give better data representation
    # compared to previous {0,1,2} representation
    GENDERS = (
        ('X', 'No answer'),
        ('F', 'Female'),
        ('M', 'Male'),
    )
    gender = models.CharField(_('gender'),
                              max_length=1,
                              choices=GENDERS,
                              default='X')
    
    ############################################################################
    # i18n/l10n
    ############################################################################
    # The preferred_language setting is not intended to force language settings
    # for users, but to give preference to particular l10n-supported elements of
    # the myRobogals service, for example in emails.
    #
    # Django's `django_language` user session key should handle the user's
    # interface language preferences for the session.
    #
    # Refer to myrg_core/settings.py for LANGUAGES
    preferred_language = models.CharField(_('preferred language'),
                                          max_length=5,
                                          choices=settings.LANGUAGES,
                                          default='en',   # This MUST exist
                                          help_text=_('Preferred language for myRobogals and related services. Interface language can be separately overridden on a session-by-session basis.'))
    
    ############################################################################
    # Contact details
    ############################################################################
    mobile = models.CharField(_('mobile number'),
                              max_length=15,
                              blank=True,
                              help_text=_('Mobile number in E.164 compatible format, of length 15 digits or fewer, without the + sign.'))
    mobile_verified = models.BooleanField(default=False)
    
    # Countries are stored in the database as a ForeignKey.
    #country = models.ForeignKey(Country,
    #    verbose_name=_('Country'),
    #    blank=True,
    #    null=True)
    postcode = models.CharField(_('postcode'),
                                max_length=15,
                                blank=True,
                                help_text=_('Postcode of residence, where applicable.'))

    ############################################################################
    # Personalisation
    ############################################################################
    # Subscriptions to newsletters, etc. Possibly extending to chapter-level
    # communications, but that may require a separate field.
    #subscriptions = models.ManyToManyField(Subscriptions,
    #    verbose_name=_('subscriptions'),
    #    blank=True,
    #    null=True)
    
    #biography = models.TextField(_('biography'),
    #    blank=True,
    #    help_text=_('Short biography of the user for their profile page.'))
    
    # ImageField requires PIL - will need to investigate if we can get something
    # like Pillow to work with Django.
    #photo = models.ImageField(upload_to='profilepics',
    #    blank=True,
    #    null=True)
    
    ############################################################################
    # Privacy and Flags
    ############################################################################
    # Privacy settings range from 0 to 99 inclusive.
    #
    # Modifications to values should be done with care as varying numbers after 
    # deployment will cause mismatching privacy level interpretations.
    PRIVACY_VISIBILITIES = (
        (0, 'Private'),
        #(10, 'Managers of your Robogals chapter'),
        #(20, 'Everyone in your Robogals chapter'),
        (50, 'Anyone in myRobogals'),
        (99, 'Public'),
    )
    
    dob_visibility = models.PositiveSmallIntegerField(_('date of birth visibility'),
                                                      choices=PRIVACY_VISIBILITIES,
                                                      default=0,
                                                      help_text=_('Level of visibility of date of birth on profile, where applicable.'))
    primary_email_visibility = models.PositiveSmallIntegerField(_('primary email address visibility'),
                                                                choices=PRIVACY_VISIBILITIES,
                                                                default=0,
                                                                help_text=_('Level of visibility of primary email address on profile.'))
    #secondary_email_visibility = models.PositiveSmallIntegerField(_('secondary email address visibility'),
    #    choices=PRIVACY_VISIBILITIES,
    #    default=0,
    #    help_text=_('Level of visibility of secondary email address on profile, where applicable.'))
    profile_visibility = models.PositiveSmallIntegerField(_('profile visibility'),
                                                          choices=PRIVACY_VISIBILITIES,
                                                          default=0,
                                                          help_text=_('Level of visibility of general profile. Overrides other profile visibility settings where visibility settings exceed that set here.'))
    
    # Generally useful Django flags
    # Note that `is_superuser` and `last_login` is already provided by
    # `AbstractBaseUser`
    is_active = models.BooleanField(_('active'),
                                    default=True,
                                    help_text=_('Designates whether this user should be treated as active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    
    # Setting the user manager to the custom class as defined above.
    objects = RobogalsUserManager()

    # USERNAME_FIELD    Primary unique identifier.
    # REQUIRED_FIELDS   Required fields, except for USERNAME_FIELD or password.
    #                   Used *only* for `createsuperuser` command.
    #                   https://docs.djangoproject.com/en/1.6/topics/auth/customizing/#django.contrib.auth.models.CustomUser.REQUIRED_FIELDS
    USERNAME_FIELD = 'primary_email'
    REQUIRED_FIELDS = [
                        'username',
                        'given_name',
                        ]
    
    
    # Fields that cannot be listed or filtered/sorted with
    PROTECTED_FIELDS = ("password","groups","user_permissions","last_login","is_superuser")

    # Fields that cannot be listed (but can be filtered/sorted with)
    # NONVISIBLE_FIELDS = ()
    
    # Fields that cannot be written to
    READONLY_FIELDS = ("id","mobile_verified","groups","user_permissions","date_joined","last_login","is_superuser","is_active")
    
    
    
    
    # Defining information for display of this class in admin
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        
    def get_full_name(self):
        """Retrieves the full name of the user in standard format.
        Use get_sortable_name() for sorting.
        Use get_preferred_name() for most other use cases.
        
        Format:
            <given> <family> (where family name available)
            <given> (otherwise)
        """
        return '{} {}'.format(self.given_name, self.family_name or '').strip()
        
    def get_sortable_name(self):
        """Retrieves the full name of the user in reverse format, suitable for
        sorting.
        
        Format:
            <family>, <given> (where family name available)
            ~, <given> (otherwise)
        """
        return '{}, {}'.format(self.family_name or '~', self.given_name)
            
    def get_preferred_name(self):
        """Retrieves the preferred name of the user, for display purposes.
        
        Format:
            <preferred> (where available)
            <given> (otherwise)
        """
        return '{}'.format(self.preferred_name or self.given_name)

    def get_short_name(self):
        return self.get_preferred_name()
    
    def get_username(self):
        "Retrieves the username of the user."
        return self.username
    
    def get_gravatar_hash(self):
        import hashlib
        return hashlib.md5(self.primary_email.lower().encode('utf-8')).hexdigest()
    
    
    
    # http://stackoverflow.com/a/6657043
    def all_unexpired_sessions(self):
        user_sessions = []
        all_sessions  = Session.objects.filter(expire_date__gte=timezone.now())
        for session in all_sessions:
            session_data = session.get_decoded()
            if self.pk == session_data.get('_auth_user_id'):
                user_sessions.append(session.pk)
        return Session.objects.filter(pk__in=user_sessions)

    def delete_all_unexpired_sessions(self):
        session_list = self.all_unexpired_sessions()
        session_list_count = len(session_list)
        session_list.delete()
        
        return session_list_count
    
    
    
    
    def __str__(self):
        return self.get_full_name()
        
    @property
    def is_staff(self):
        # We are implying superusers = staff
        return self.is_superuser
