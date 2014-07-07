from .models import Group, RoleClass, Role

from rest_framework import serializers

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        read_only_fields = model.READONLY_FIELDS
        write_only_fields = model.PROTECTED_FIELDS
        
class RoleClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoleClass
        read_only_fields = RoleClass.READONLY_FIELDS
        write_only_fields = RoleClass.PROTECTED_FIELDS
        
class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        read_only_fields = Role.READONLY_FIELDS
        write_only_fields = Role.PROTECTED_FIELDS