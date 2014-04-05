"""
    myRobogals
    myrg_repo/models.py
    Custom RepoContainer, RepoFile model definition

    2014
    Robogals Software Team
"""

from django.db import models
from django.core import validators
from django.utils import timezone
from myrg_users.models import RobogalsUser
from myrg_groups.models import Role

class RepoContainer(models.Model):
    user = models.ForeignKey('RobogalsUser')
    role = models.ForeignKey('Role')
    title = models.CharField(_('title'),
                             blank=False)
    body = models.TextField(_('body'),
                            blank=False)
    tags = models.CharField(_('tags'),
                            blank=False)
    SERVICE_CHOICES = (
        (0, 'Private'), #Default, but we will probably disallow this in logic. We don't want people hiding files on our server.
        (10, 'Managers of your Robogals chapter'),
        (20, 'Everyone in your Robogals chapter'),
        (50, 'All Robogals chapters'),
        (99, 'Public'),
    )
    service = models.PositiveSmallIntegerField(_('service'),
                                               choices=SERVICE_CHOICES,
                                               default=0,
                                               blank=False)
    date_created = models.DateField(_('date created'),
                                    blank=False)
    date_updated = models.DateField(_('date created'),
                                    blank=False)

class RepoFile(models.Model):
    name = models.CharField(_('name'),
                            blank=False)
    file = models.FileField(_('file'),
                            blank=False)
    container = models.ForeignKey('RepoContainer')