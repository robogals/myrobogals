from myrg_groups.models import RoleType, Role

from rest_framework import serializers

class RoleTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = RoleType
        fields = ('name', 'description', 'group_exclude', 'group_include',)

class RoleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Role
        fields = ('user', 'role_type', 'group', 'date_start', 'date_end',)

