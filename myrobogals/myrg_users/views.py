from django.contrib.auth.models import Group
from .models import RobogalsUser

from rest_framework import viewsets
from .serializers import RobogalsUserSerializer, GroupSerializer
    
class RobogalsUserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = RobogalsUser.objects.all()
    serializer_class = RobogalsUserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


