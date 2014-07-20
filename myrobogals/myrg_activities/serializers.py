from .models import Activity

from rest_framework import serializers

class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        read_only_fields = Activity.READONLY_FIELDS
        write_only_fields = Activity.PROTECTED_FIELDS
