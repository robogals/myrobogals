from __future__ import unicode_literals
from future.builtins import *
import six
from django.utils.encoding import python_2_unicode_compatible

from django.db import models
from django.core import validators
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from myrg_users.models import RobogalsUser
from myrg_groups.models import Role

#@python_2_unicode_compatible
class RepoContainer(models.Model):
    def uuid_generator():
        from uuid import uuid4
        return str(uuid4().hex)
    
    id = models.CharField(max_length=32, 
                          primary_key=True, 
                          default=uuid_generator)
    user = models.ForeignKey(RobogalsUser)
    role = models.ForeignKey(Role)
    title = models.CharField(_('title'),
                             max_length=63,
                             blank=False)
    body = models.TextField(_('body'),
                            blank=False)
    tags = models.CharField(_('tags'),
                            max_length=63,
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
                                               default=99,
                                               blank=False
                                               )
    date_created = models.DateTimeField(_('date created'),
                                    blank=False,
                                    default=timezone.now)
    date_updated = models.DateTimeField(_('date updated'),
                                    blank=False,
                                    default=timezone.now)
    
    # Fields that cannot be listed or filtered/sorted with
    PROTECTED_FIELDS = ()

    # Fields that cannot be listed (but can be filtered/sorted with)
    # NONVISIBLE_FIELDS = (
    
    # Fields that cannot be written to
    READONLY_FIELDS = ("id","date_created",)
    
    def __str__(self):
        return self.title

#@python_2_unicode_compatible
class RepoFile(models.Model):
    name = models.CharField(_('name'),
                            max_length=63,
                            blank=False)
    file = models.FileField(_('file'),
                            upload_to='repo-files',
                            blank=False
                            )
    container = models.ForeignKey(RepoContainer)
    
    # Fields that cannot be listed or filtered/sorted with
    PROTECTED_FIELDS = ()

    # Fields that cannot be listed (but can be filtered/sorted with)
    # NONVISIBLE_FIELDS = ()
    
    # Fields that cannot be written to
    READONLY_FIELDS = ("id",)
    
    def __str__(self):
        return self.name