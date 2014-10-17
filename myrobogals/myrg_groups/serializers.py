from __future__ import unicode_literals
from future.builtins import *
import six

from .models import Group, Chapter, School, Company, RoleClass, Role

from rest_framework import serializers

class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        if fields:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields.keys())
            #import pdb; pdb.set_trace()
            for field_name in existing - allowed:
                self.fields.pop(field_name)

class GroupSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Group
        read_only_fields = model.READONLY_FIELDS
        write_only_fields = model.PROTECTED_FIELDS
        
class ChapterSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Chapter
        read_only_fields = model.READONLY_FIELDS
        write_only_fields = model.PROTECTED_FIELDS
        
class SchoolSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = School
        read_only_fields = model.READONLY_FIELDS
        write_only_fields = model.PROTECTED_FIELDS
        
class CompanySerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Company
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
