#from django.forms import widgets
from django.contrib.auth.models import User, Group
from rest_framework import serializers
from api_1_0.models import User

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        #fields = ('url', 'username', 'email', 'groups')
# Bagus comment: I modified this fields to adjust with the user class in models.py
        fields = ('url', 'username', 'first_name', 'last_name', 'email', 'password', 'is_staff', 'is_active', 'is_superuser', 'last_login', 'date_joined', 'user_permissions')


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')