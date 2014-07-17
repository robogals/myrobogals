"""
    myRobogals
    myrg_activities/models.py
    Custom Activity, Subactivity, Participant, PecuniaryTransaction
    Item model definition

    2014
    Robogals Software Team
"""

from django.db import models
from django.utils.translation import ugettext_lazy as _

# Create your models here.
class Activity(models.Model):
    id = models.CharField(_('id'),
                          blank=False,
                          unique=True,
                          primary_key=True)
    name = models.CharField(_('name'),
                            blank=False)
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
    creator_role = models.ForeignKey('role')
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
                                blank=False,
                                default='XXX')
    tax_rate = models.FloatField(_('tax rate'),
                                 blank=False,
                                 default=0.00)

class SubActivity(models.Model):
    id = models.CharField(_('id'),
                          blank=False,
                          unique=True,
                          primary_key=True)
    parent = models.ForeignKey('activity')
    name = models.CharField(_('name'),
                            blank=False)
    description = models.TextField(_('description'))
    date_rsvp_open = models.DateTimeField(_('date rsvp open'),
                                          blank=False)
    date_rsvp_close = models.DateTimeField(_('date rsvp close'),
                                          blank=False)
    date_activity_start = models.DateTimeField(_('date activity start'),
                                          blank=False)
    date_activity_end = models.DateTimeField(_('date activity end'),
                                          blank=False)

class Participant(models.Model):
    id = models.CharField(_('id'),
                          blank=False,
                          unique=True,
                          primary_key=True)
    activity = models.ForeignKey('activity')
    user_role = models.ForeignKey('role')
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
                                        blank=False)

class PecuniaryTransaction(models.Model):
    date = models.DateTimeField(_('date'),
                                blank=False,
                                auto_now=True)
    initiator_role = models.ForeignKey('role')
    participant = models.ForeignKey('participant')
    label = models.CharField(_('label'),
                             blank=False)
    description = models.TextField(_('description'))
    amount = models.FloatField(_('amount'),
                               blank=False)

class Item(models.Model):
    activity = models.ForeignKey('activity')
    name = models.CharField(_('name'),
                            blank=False)
    definition = models.TextField(_('definition'),
                                  blank=False)
    order = models.PositiveIntegerField(_('display order'),
                                        default=0)
    date_open = models.DateTimeField(_('date open'),
                                     blank=False)
    date_close = models.DateTimeField(_('date close'),
                                      blank=False)