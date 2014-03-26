"""
    myRobogals
    myrg_groups/models.py

    2014
    Robogals Software Team
"""

from django.db import models
from django.core import validators
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import Group
from myrg_users.models import RobogalsUser

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

    def applicableGroups(self):
        if self.group_include.all():
            applGroups = self.group_include.exclude(pk__in = self.group_exclude.all())
        else:
            applGroups = Group.objects.exclude(pk__in = self.group_exclude.all())
        return applGroups

class Role(models.Model):
    user = models.ForeignKey(RobogalsUser)
    role_type = models.ForeignKey(RoleType)
    group = models.ForeignKey(Group)

    date_start = models.DateTimeField(_('date start'),
        default=timezone.now)

    date_end = models.DateTimeField(_('date end'),
        blank=True,
        null=True)
