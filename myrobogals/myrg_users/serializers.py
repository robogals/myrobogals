from .models import RobogalsUser

from rest_framework import serializers

class RobogalsUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = RobogalsUser
        read_only_fields = RobogalsUser.READONLY_FIELDS
        write_only_fields = RobogalsUser.PROTECTED_FIELDS

    def restore_object(self, attrs, instance=None):
        if instance is None:
            instance = self.opts.model()
            
        for key, val in attrs.items():
            try:
                if key == "password":
                    instance.set_password(attrs.get('password', instance.password))
                else:
                    setattr(instance, key, val)
            except ValueError:
                self._errors[key] = self.error_messages['required']

        return instance