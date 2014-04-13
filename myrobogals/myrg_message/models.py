"""
    myRobogals
    myrg_message/models.py
    Custom Message, MessageDefinition model definition

    2014
    Robogals Software Team
"""

from django.db import models
from django.core import validators
from django.utils import timezone
from myrg_users.models import RobogalsUser
from myrg_groups.models import Role

class MessageDefinition(models.Model):
    sender = models.ForeignKey(RobogalsUser)
    sender_role = models.ForeignKey(Role)
    sender_manual = models.CharField(_('sender manual'),
                                     blank=True)
    subject = models.CharField(_('subject'),
                               blank=True)
    body = models.TextField(_('body'),
                            blank=False)
    variables = models.TextField(_('variables'),
                                 blank=False)
    attachments = models.TextField(_('attachments'),
                                   blank=False)
    SERVICE_CHOICES = (
        (1, 'Mandrill'), #Default
        (2, 'SMSGlobal')
    )
    service = models.PositiveSmallIntegerField(_('service'),
                                               choices=SERVICE_CHOICES,
                                               default=1,
                                               blank=False)
    date_created = models.DateField(_('date created'),
                                    blank=False)

class Message(models.Model):
    definition = models.ForeignKey(MessageDefinition)
    recipient_user = models.ForeignKey(RobogalsUser,
                                       blank=True,
                                       null=True)
    recipient_manual = models.CharField(_('recipient manual'),
                                        blank=True)
    service_id = models.CharField(_('service id'),
                                  blank=True)
    service_status = models.CharField(_('service status'),
                                      blank=True)
    date_created = models.DateField(_('date created'),
                                    blank=False)
    date_delivered = models.DateField(_('date delivered'),
                                      blank=False)