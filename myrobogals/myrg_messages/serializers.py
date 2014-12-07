from __future__ import unicode_literals
from future.builtins import *
import six

from .models import EmailDefinition, SMSDefinition, EmailMessage, SMSMessage

from myrg_groups.serializers import DynamicFieldsModelSerializer

from rest_framework import serializers

class EmailDefinitionSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = EmailDefinition
        read_only_fields = model.READONLY_FIELDS
        write_only_fields = model.PROTECTED_FIELDS

class EmailMessageSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = EmailMessage
        read_only_fields = model.READONLY_FIELDS
        write_only_fields = model.PROTECTED_FIELDS
