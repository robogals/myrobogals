from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from api_1_0.serializers import UserSerializer, GroupSerializer
from api_1_0.models import User #Bagus comment: I Added this to call the user Class


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer