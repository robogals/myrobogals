from django.shortcuts import render

from rest_framework import viewsets
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer

from myrg_groups.models import RoleType, Role
from myrg_groups.serializers import RoleTypeSerializer, RoleSerializer

class RoleTypeViewSet(viewsets.ModelViewSet):
    queryset = RoleType.objects.all()
    serializer_class = RoleTypeSerializer

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
