from django.db import models
from django.utils.translation import ugettext_lazy as _
from myrg_groups.models import RoleClass


class PermissionDefinition(models.Model):
    role_class = models.OneToOneField(RoleClass)
    definition = models.TextField(_('definition'),
                                  blank=False,
                                  help_text=_('Json list of permission key-value pairs or just a list for positive permissions.'))

