"""
    myRobogals
    myrg_core/models.py
    Custom APILog model definition

    2014
    Robogals Software Team
"""

from django.db import models
from django.core import validators
from django.utils import timezone

class APILog(models.Model):
    user = models.ForeignKey(_('user'),
                             blank=True
                             null=True)
    role = models.ForeignKey(_('role'),
                             blank=True
                             null=True)
    api_url = models.CharField(_('api url'),
                               blank=False)
    api_call = models.TextField(_('api call'),
                                blank=False)
    date = models.DateTimeField(_('date'),
                                blank=False,
                                default=timezone.now)