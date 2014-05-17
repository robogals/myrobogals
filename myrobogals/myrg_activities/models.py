"""
    myRobogals
    myrg_activities/models.py
    Custom Activity, Invitation, Participant, PecuniaryItem,
    PecuniaryTransaction, Question, QuestionResponse model definition

    2014
    Robogals Software Team
"""

from django.db import models
from django.utils import timezone

class Activity(models.Model):
    id = models.CharField(_('id'),
                          blank=False,
                          unique=True,
                          primary_key=True)
    # todo: a generator function to generate random 128-bit IDs as necessary
    # (This shall replace Django's own internal ID system, by giving minimum 128-bit IDs, hex encoded.)
    name = models.CharField(_('name'),
                            blank=False)
    preferred_name = models.CharField(_('preferred name'),
                                      blank=True)
    description = models.TextField(_('description'),
                                   blank=True)
    location = models.TextField(_('location'),
                                blank=False) # todo: json
    TYPE_CHOICES = (
        (0, 'Standard'),
        (1, 'Workshop'),
        (2, 'Training event'),
        (3, 'Conference'),
    )
    type = models.IntegerField(_('type'),
                                 choices=TYPE_CHOICES,
                                 blank=False,
                                 default=0)
    parent = models.ForeignKey('self',
                               null=True,
                               blank=True)
    STATUS_CHOICES = (
        (0, 'Inactive'),
        (3, 'Active, Manually Entered Participants'),
        (5, 'Active, Select Invitation'),
        (8, 'Active, Open Invitation, Hidden'),
        (9, 'Active, Open Invitation, Publicly Visible'),
    )
    status = models.IntegerField(_('status'),
                                 choices=STATUS_CHOICES,
                                 blank=False,
                                 default=0)
    creator = models.ForeignKey('RobogalsUser')
    creator_role = models.ForeignKey('Role')
    date_created = models.DateField(_('date created'),
                                    blank=False)
    date_invitation_open = models.DateField(_('date invitation open'),
                                            blank=False)
    date_invitation_close = models.DateField(_('date invitation close'),
                                             blank=True)
    date_activity_start = models.DateField(_('date activity start'),
                                           blank=False)
    date_activity_end = models.DateField(_('date activity end'),
                                         blank=False)
    currency = models.CharField(_('currency'),
                                blank=True,
                                length=3,
                                help_text=_('ISO 4217 codes only.'))

class Invitation(models.Model):
    id = models.CharField(_('id'),
                          blank=False,
                          unique=True,
                          primary_key=True)
    # todo: a generator function to generate random 128-bit IDs as necessary
    # (This shall replace Django's own internal ID system, by giving minimum 128-bit IDs, hex encoded.)
    activity = models.ForeignKey('Activity')
    user = models.ForeignKey('RobogalsUser')
    STATUS_CHOICES = (
        (0, 'Invalid'),
        (1, 'Valid'),
    )
    status = models.IntegerField(_('status'),
                                 choices=STATUS_CHOICES,
                                 blank=False,
                                 default=0)

class Participant(models.Model):
    id = models.CharField(_('id'),
                          blank=False,
                          unique=True,
                          primary_key=True)
    # todo: a generator function to generate random 128-bit IDs as necessary
    # (This shall replace Django's own internal ID system, by giving minimum 128-bit IDs, hex encoded.)
    activity = models.ForeignKey('Activity')
    user = models.ForeignKey('RobogalsUser')
    role = models.ForeignKey('Role')
    STATUS_CHOICES = (
        (0, 'Invalid'),
        (1, 'Valid'),
    )
    status = models.IntegerField(_('status'),
                                 choices=STATUS_CHOICES,
                                 blank=False,
                                 default=0)

class PecuniaryItem(models.Model):
    activity = models.ForeignKey('Activity')
    name = models.CharField(_('name'),
                            blank=False)
    description = models.TextField(_('Description'),
                                   blank=True)
    amount = models.FloatField(_('Amount'),
                               blank=False)
    date_start = models.DateField(_('date start'),
                                  blank=False)
    date_end = models.DateField(_('date end'),
                                blank=False)
    variable_quantity = models.BooleanField(_('variable quantity'),
                                            blank=False,
                                            default=False)
    default_quantity = models.FloatField(_('default quantity'),
                                         blank=True,
                                         default=1)
    STATUS_CHOICES = (
        (0, 'Invalid'),
        (1, 'Valid'),
    )
    status = models.IntegerField(_('status'),
                                 choices=STATUS_CHOICES,
                                 blank=False,
                                 default=0)
    order = models.PositiveIntegerField(_('order'),
                                        blank=False,
                                        default=0)

class PecuniaryTransaction(models.Model):
    date = models.DateTimeField(_('date'),
                                blank=False,
                                auto_now=True)
    activity = models.ForeignKey('Activity')
    initiator = models.ForeignKey('RobogalsUser',
                                  help_text=_('The user *applying* the transaction'))
    participant = models.ForeignKey('Participant',
                                    help_text=_('The user against which the transaction is held against'))
    label = models.CharField(_('Label'),
                             blank=False)
    description = models.TextField(_('Description'),
                                   blank=True)
    amount = models.FloatField(_('Amount'),
                               blank=False)


class Question(models.Model):
    acitivity = models.ForeignKey('Activity')
    name = models.CharField(_('name'),
                            blank=False)
    body = models.TextField(_('body'),
                            blank=False,
                            help_text=_('Will contain question HTML content'))
    definition = models.TextField(_('definition'),
                                  blank=False)
    required = models.BooleanField(_('required'),
                                   blank=False)
    order = models.PositiveIntegerField(_('order'),
                                        blank=False
                                        default=0)

class QuestionResponse(models.Model):
    question = models.ForeignKey('Question')
    participant = models.ForeignKey('Participant')
    response = models.TextField(_('response'),
                                blank=False)
    