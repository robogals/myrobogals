from django.db import models
from pytz import timezone


class University(models.Model):
    name = models.CharField(max_length=64)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('name',)
        verbose_name = "university"
        verbose_name_plural = "universities"


class Country(models.Model):
    code = models.CharField("ISO 3166-1 code", max_length=2, primary_key=True)
    country_name = models.CharField("Country", max_length=128)

    def __unicode__(self):
        return self.country_name

    class Meta:
        ordering = ('country_name', 'code')
        verbose_name_plural = 'countries'


class Subdivision(models.Model):
    code = models.CharField("ISO 3166-2 code", max_length=3)
    country = models.ForeignKey(Country)
    subdivision_name = models.CharField("Name", max_length=128)

    def __unicode__(self):
        return self.subdivision_name

    def full_iso_code(self):
        return str(self.country.pk) + "-" + self.code

    class Meta:
        ordering = ('subdivision_name',)


class Timezone(models.Model):
    description = models.CharField(max_length=64)

    def __unicode__(self):
        return self.description

    def tz_obj(self):
        return timezone(self.description)

    class Meta:
        ordering = ['description', ]


class MobileRegexCollection(models.Model):
    description = models.CharField(max_length=64)
    errmsg = models.CharField(max_length=128)

    def __unicode__(self):
        return self.description


class MobileRegex(models.Model):
    collection = models.ForeignKey(MobileRegexCollection)
    regex = models.CharField(max_length=200)
    description = models.CharField(max_length=64)
    strip_digits = models.SmallIntegerField(default=0)
    prepend_digits = models.CharField(max_length=16, blank=True)

    def __unicode__(self):
        return self.regex

    class Meta:
        verbose_name_plural = 'Mobile regexes'


# Import and register the signal handlers in signals.py
import signals
