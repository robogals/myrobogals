from __future__ import unicode_literals
from future.builtins import *
import six



from .models import RobogalsUser

from rest_framework import serializers

class RobogalsUserSerializer(serializers.ModelSerializer):
    display_name = serializers.Field(source='get_preferred_name')
    gravatar_hash = serializers.Field(source='get_gravatar_hash')
    
    class Meta:
        model = RobogalsUser
        read_only_fields = RobogalsUser.READONLY_FIELDS
        write_only_fields = RobogalsUser.PROTECTED_FIELDS

    def restore_object(self, attrs, instance=None):
        if instance is None:
            instance = self.opts.model()
            
        for key, val in six.iteritems(attrs):
            try:
                if key == "password":
                    instance.set_password(attrs.get('password', instance.password))
                else:
                    setattr(instance, key, val)
            except ValueError:
                self._errors[key] = self.error_messages['required']

        return instance
        
    