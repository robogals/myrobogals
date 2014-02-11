from django.contrib.auth.models import User, Group
from rest_framework import serializers
#from api_1_0.models import Profile

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'first_name', 'last_name', 'email', 'groups', 'is_staff', 'is_active', 'is_superuser', 'last_login', 'date_joined')
# Bagus comment: I modified this fields to adjust with the user class

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')

