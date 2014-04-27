from django.db import models

from myrg_groups.models import RoleType


class PermissionDefinition(models.Model):
    role_type = models.ForeignKey(RoleType)
    definition = models.TextField(_('definition'),
                                  blank=False,
                                  help_text=_('Json list of permission key-value pairs or just a list for positive permissions.'))

