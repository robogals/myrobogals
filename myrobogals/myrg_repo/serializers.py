from __future__ import unicode_literals
from future.builtins import *
import six

from .models import RepoContainer, RepoFile

from rest_framework import serializers
        
class RepoContainerSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepoContainer
        read_only_fields = RepoContainer.READONLY_FIELDS
        write_only_fields = RepoContainer.PROTECTED_FIELDS
        
class RepoFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepoFile
        search_fields = ['repofile__container']
        read_only_fields = RepoFile.READONLY_FIELDS
        write_only_fields = RepoFile.PROTECTED_FIELDS