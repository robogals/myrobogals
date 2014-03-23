"""
    myRobogals
    myrg_groups/model.py
    Custom RobogalsGroup and RobogalsChapter model definition

    2014
    Robogals Software Team
"""

from django.db import models
from django.core import validators

# Based upon:
# * https://docs.djangoproject.com/en/dev/ref/models/fields/

class RobogalsGroup(models.Model):
    name = models.CharField(_('name'),
                            blank=False)
    preferred_name = models.CharField(_('preferred name'),
                                      blank=True)

    parent = models.ForeignKey('self',
                               null=True,
                               blank=True)

    STATUS_CHOICES = (
        (0, 'Inactive'),
        (1, 'Hidden'),
        (8, 'Active, Non-joinable'),
        (9, 'Active, Joinable'),
    )
    status = models.CharField(_('status'),
                              choices=STATUS_CHOICES,
                              default=0,
                              blank=False)

    date_created = models.DateField(_('date created'),
                                    blank=False)

class RobogalsChapter(models.Model):
    group = models.ForeignKey(Group)

    university = models.CharField(_('university'),
                                  blank=True)

    address = models.CharField(_('address'),
                               blank=False)
    city = models.CharField(_('city'),
                            blank=True)
    state = models.CharField(_('state'),
                             blank=True)
    postcode = models.CharField(_('postcode'),
                                blank=True,
                                max_length=16)
    country = models.CharField(_('country'),
                               blank=False)
    latitude = models.FloatField(_('latitude'),
                                 blank=True)
    longitude = models.FloatField(_('longitude'),
                                  blank=True)

    timezone = models.CharField(_('timezone'),
                                blank=False,
                                default='Etc/UTC')

    url = models.CharField(_('url'),
                           blank=True)
    html = models.TextField(_('html'),
                            blank=True,
                            help_text=_('Holds HTML content for chapter info page and is different from an actual website.'))
