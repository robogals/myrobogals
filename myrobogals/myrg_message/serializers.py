from myrg_message.models import Message, MessageDefinition

from rest_framework import serializers

class MessageDefinitionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MessageDefinition
        fields = ('sender', 'sender_role', 'sender_manual', 'subject', 'body', 'variables', 'attachments', 'service', 'date_created',)

class MessageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Message
        fields = ('definition', 'recipient_user', 'recipient_manual', 'service_id', 'service_status', 'date_created', 'date_delivered',)
