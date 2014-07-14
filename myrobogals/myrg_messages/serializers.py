from .models import EmailDefinition, SMSDefinition, EmailMessage, SMSMessage

from rest_framework import serializers

class EmailDefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailDefinition
        read_only_fields = model.READONLY_FIELDS
        write_only_fields = model.PROTECTED_FIELDS