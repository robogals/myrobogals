from .models import RobogalsUser
from myrg_groups.models import Group

from rest_framework import serializers

class RobogalsUserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = RobogalsUser
        fields = ('url', 'username', 'given_name', 'primary_email', 'groups', 'is_active', 'is_superuser',)

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('name', 'preferred_name', 'parent', 'status', 'date_created',)

