from __future__ import unicode_literals
from future.builtins import *
import six
from django.utils.encoding import python_2_unicode_compatible

from django.db import models
from django.utils.translation import ugettext_lazy as _
from myrg_groups.models import RoleClass


#@python_2_unicode_compatible
class PermissionDefinition(models.Model):
    role_class = models.OneToOneField(RoleClass)
    definition = models.TextField(_('definition'),
                                  blank=False,
                                  help_text=_('Json list of permission key-value pairs or just a list for positive permissions.'))

#@python_2_unicode_compatible
class PermissionList(models.Model):
    permission = models.TextField(_('permission'),
                                  blank=False,
                                  help_text=_('permission naming structure: [Core function/thing]_[Component/Visibility]_[Action]. e.g: USER_SELF_VIEW'))
    role_classes = models.CommaSeparatedIntegerField(max_length=200)
    