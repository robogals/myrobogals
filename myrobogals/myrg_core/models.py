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
    role = models.ForeignKey(_('role'),
                             blank=True
                             null=True)
    api_url = models.CharField(_('api url'),
                               blank=False)
    api_call = models.TextField(_('api call'),
                                blank=False)
    note = models.TextField(_('note'),
                            blank=True,
                            null=True)
    date = models.DateTimeField(_('date'),
                                blank=False,
                                auto_now_add=True)