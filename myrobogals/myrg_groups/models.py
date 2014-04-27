"""
    myRobogals
    myrg_groups/models.py
    Custom LocatableEntity, Role, RoleType model definition

    2014
    Robogals Software Team
"""

from django.db import models
from django.core import validators
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from myrg_users.models import RobogalsUser



# Based upon:
# * https://docs.djangoproject.com/en/dev/ref/models/fields/

class Group(models.Model):
    name = models.CharField(_('name'), blank=False)
    preferred_name = models.CharField(_('preferred name'),
                                      blank=True)

    parent = models.ForeignKey('self',
                               null=True,
                               blank=True)

    STATUS_CHOICES = (
        (0, 'Inactive'),
        (1, 'Hidden'),
        (8, 'Active, Non-joinable'),
        (9, 'Active, Joinable'),
    )
    status = models.PositiveSmallIntegerField(_('status'),
                              choices=STATUS_CHOICES,
                              default=0,
                              blank=False)

    date_created = models.DateField(_('date created'),
                                    blank=False)

class LocatableEntity(models.Model):
    group = models.ForeignKey(Group)
    address = models.CharField(_('address'),
                               blank=False)
    city = models.CharField(_('city'),
                            blank=True)
    state = models.CharField(_('state'),
                             blank=True)
    postcode = models.CharField(_('postcode'),
                                blank=True,
                                max_length=16)
    country = models.CharField(_('country'),
                               blank=False)
    latitude = models.FloatField(_('latitude'),
                                 blank=True)
    longitude = models.FloatField(_('longitude'),
                                  blank=True)

    timezone = models.CharField(_('timezone'),
                                blank=False,
                                default='Etc/UTC')

    url = models.CharField(_('url'),
                           blank=True)
    html = models.TextField(_('html'),
                            blank=True,
                            help_text=_('Holds HTML content for chapter info page and is different from an actual website.'))

class Chapter(LocatableEntity):
    university = models.CharField(_('university'),
                                  blank=True)

class School(LocatableEntity):
    pass

class Company(LocatableEntity):
    legal_name = models.CharField(_('legal name'),
                                  blank=True)

class RoleType(models.Model):
    name = models.CharField(_('name'),
        max_length=63,
        unique=True,
        validators=[
            validators.RegexValidator(r'^[\w.-]+$', _('This value may contain only alphanumeric and ./_/- characters.'), 'invalid')
        ],
        help_text=_('Name of length 63 characters or fewer, consisting of alphanumeric characters and any of ./_/- is required.'))

    description = models.TextField(_('description'),
        blank=True,
        help_text=_('Short description of the role type.'))

    group_exclude = models.ManyToManyField(Group,
        related_name='roletype_exclude',
        blank=True,
        null=True)

    group_include = models.ManyToManyField(Group,
        related_name='roletype_include',
        blank=True,
        null=True)

    def __unicode__(self):
        return self.name

    def get_applicable_groups(self):
        if self.group_include.all():
            applicable_groups = self.group_include.exclude(pk__in = self.group_exclude.all())
        else:
            applicable_groups = Group.objects.exclude(pk__in = self.group_exclude.all())
        return applicable_groups

class Role(models.Model):
    user = models.ForeignKey(RobogalsUser)
    role_type = models.ForeignKey(RoleType)
    group = models.ForeignKey(Group)

    date_start = models.DateTimeField(_('date start'),
        default=timezone.now)

    date_end = models.DateTimeField(_('date end'),
        blank=True,
        null=True)




