from __future__ import unicode_literals
from future.builtins import *
import six

from .models import PermissionList

from rest_framework import serializers
        
class PermissionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PermissionList
        