from __future__ import unicode_literals
from future.builtins import *
import six
from django.utils.encoding import python_2_unicode_compatible


from django.db import models
from django.utils.translation import ugettext_lazy as _

from myrg_groups.models import Role

@python_2_unicode_compatible
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