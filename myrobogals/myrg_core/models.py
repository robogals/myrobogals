"""
    myRobogals
    myrg_core/models.py
    Custom APILog model definition

    2014
    Robogals Software Team
"""

from django.db import models
from django.utils.translation import ugettext_lazy as _

from myrg_groups.models import Role

class APILog(models.Model):
    user_role = models.ForeignKey(Role,
                             blank=True,
                             null=True)
    ip = models.CharField(_('ip address'),
                            max_length=63,
                           blank=False)
    api_url = models.CharField(_('api url'),
                                max_length=255,
                               blank=False)
    api_body = models.TextField(_('api body'),
                                blank=False)
    note = models.TextField(_('note'),
                            blank=True,
                            null=True)
    date = models.DateTimeField(_('date'),
                                blank=False,
                                auto_now_add=True)