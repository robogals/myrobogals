from __future__ import unicode_literals
from future.builtins import *
import six
from django.utils.encoding import python_2_unicode_compatible

from django.db import models
from django.utils.translation import ugettext_lazy as _

from myrg_users.models import RobogalsUser
from myrg_groups.models import Role

#@python_2_unicode_compatible
class Activity(models.Model):
    def uuid_generator():
        from uuid import uuid4
        return str(uuid4().hex)
    
    id = models.CharField(max_length=32, primary_key=True, default=uuid_generator)
    
    name = models.CharField(_('name'),
                            blank=False,
                            max_length=127)
    description = models.TextField(_('description'))
    location = models.TextField(_('location'))
    STATUS_CHOICES = (
        (0, 'Deleted'),
        (1, 'Inactive'),
        
        (2, 'Active, Private, Non-joinable'),
        (3, 'Active, Private, Gated'),
        (4, 'Active, Private, Joinable'),
        
        (7, 'Active, Public, Non-joinable'),
        (8, 'Active, Public, Gated'),
        (9, 'Active, Public, Joinable'),
    )
    status = models.PositiveSmallIntegerField(_('status'),
                              choices=STATUS_CHOICES,
                              default=0,
                              blank=False)
                              
    creator_role = models.ForeignKey(Role)
    
    date_created = models.DateTimeField(_('date created'),
                                        blank=False)
    date_rsvp_open = models.DateTimeField(_('date rsvp open'),
                                        blank=False)
    date_rsvp_close = models.DateTimeField(_('date rsvp close'),
                                        blank=False)
    date_activity_start = models.DateTimeField(_('date activity start'),
                                        blank=False)
    date_activity_end = models.DateTimeField(_('date activity end'),
                                        blank=False)
    currency = models.CharField(_('currency'),
                                max_length=3,
                                blank=False,
                                default='XXX')
    tax_rate = models.FloatField(_('tax rate'),
                                 blank=False,
                                 default=0.00)
    
    # Fields that cannot be listed or filtered/sorted with
    PROTECTED_FIELDS = ()

    # Fields that cannot be listed (but can be filtered/sorted with)
    # NONVISIBLE_FIELDS = ()
    
    # Fields that cannot be written to
    READONLY_FIELDS = ("id",)

    
    def __str__(self):
        return self.name

#@python_2_unicode_compatible
class SubActivity(models.Model):
    def uuid_generator():
        from uuid import uuid4
        return str(uuid4().hex)
    
    id = models.CharField(max_length=32, primary_key=True, default=uuid_generator)
    
    parent = models.ForeignKey(Activity)
    
    name = models.CharField(_('name'),
                            blank=False,
                            max_length=127)
    description = models.TextField(_('description'))
    date_rsvp_open = models.DateTimeField(_('date rsvp open'),
                                          blank=False)
    date_rsvp_close = models.DateTimeField(_('date rsvp close'),
                                          blank=False)
    date_activity_start = models.DateTimeField(_('date activity start'),
                                          blank=False)
    date_activity_end = models.DateTimeField(_('date activity end'),
                                          blank=False)
    
    # Fields that cannot be listed or filtered/sorted with
    PROTECTED_FIELDS = ()

    # Fields that cannot be listed (but can be filtered/sorted with)
    # NONVISIBLE_FIELDS = ()
    
    # Fields that cannot be written to
    READONLY_FIELDS = ("id",)
    
    def __str__(self):
        return self.name
        
        
@python_2_unicode_compatible
class Participant(models.Model):
    def uuid_generator():
        from uuid import uuid4
        return str(uuid4().hex)
    
    id = models.CharField(max_length=32, primary_key=True, default=uuid_generator)
    activity = models.ForeignKey(Activity)
    user_role = models.ForeignKey(Role)
    STATUS_CHOICES = (
        (0, 'Neutral'),
        (1, 'Negative'),
        (9, 'Positive'),
    )
    status = models.PositiveSmallIntegerField(_('status'),
                              choices=STATUS_CHOICES,
                              default=0,
                              blank=False)
    response = models.TextField(_('response'))
    last_changed = models.DateTimeField(_('last_changed'),
                                        blank=False,
                                        auto_now=True)
    
    # Fields that cannot be listed or filtered/sorted with
    PROTECTED_FIELDS = ()

    # Fields that cannot be listed (but can be filtered/sorted with)
    # NONVISIBLE_FIELDS = ()
    
    # Fields that cannot be written to
    READONLY_FIELDS = ("id",)
                                        
    def __str__(self):
        return self.user_role
        
        
#@python_2_unicode_compatible
class PecuniaryTransaction(models.Model):
    date = models.DateTimeField(_('date'),
                                blank=False,
                                auto_now_add=True)
    initiator_role = models.ForeignKey(Role)
    participant = models.ForeignKey(Participant)
    label = models.CharField(_('label'),
                             blank=False,
                            max_length=127)
    description = models.TextField(_('description'))
    amount = models.FloatField(_('amount'),
                               blank=False)

#@python_2_unicode_compatible
class Item(models.Model):
    name = models.CharField(_('name'),
                            blank=False,
                            max_length=127)
    definition = models.TextField(_('definition'),
                                  blank=False)
    order = models.PositiveIntegerField(_('display order'),
                                        default=0)
    date_open = models.DateTimeField(_('date open'),
                                     blank=False)
    date_close = models.DateTimeField(_('date close'),
                                      blank=False)
                                      
    class Meta:
        abstract = True

#@python_2_unicode_compatible
class ActivityItem(Item):
    activity = models.ForeignKey(Activity)

#@python_2_unicode_compatible
class SubActivityItem(Item):
    subactivity = models.ForeignKey(SubActivity)
    
    