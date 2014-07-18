from myrg_core.classes import RobogalsAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from django.db.models import Q
from django.utils import timezone

from .functions import send_email



MAX_MESSAGES = 1






class SendMessage(RobogalsAPIView):
    def post(self, request, format=None):
        # request.user
        role_id = request.DATA.get("role")
        
        # Build query
        try:
            user_query = request.user
            
            if not (role_id is None):
                role_query = user_query.role_set.filter(Q(date_start__lte=timezone.now()) & (Q(date_end__isnull=True) | Q(date_end__gte=timezone.now()))).get(pk = str(role_id))
        except:
            return Response({"detail":"ROLE_INVALID"}, status=status.HTTP_400_BAD_REQUEST)
    
    
        # request.DATA
        try:
            supplied_messages = list(request.DATA.get("message"))
        except:
            return Response({"detail":"DATA_FORMAT_INVALID"}, status=status.HTTP_400_BAD_REQUEST)

            
        if len(supplied_messages) > MAX_MESSAGES:
            return Response({"detail":"REQUEST_OVER_OBJECT_LIMIT"}, status=status.HTTP_400_BAD_REQUEST)

        failed_messages = {}
        completed_messages = {}
            
        for message_object in supplied_messages:
            skip_message = False

            
            try:
                message_nonce = message_object.get("nonce")
                message_data = dict(message_object.get("data"))
            except:
                return Response({"detail":"DATA_FORMAT_INVALID"}, status=status.HTTP_400_BAD_REQUEST)
            
            if (message_nonce is None):
                return Response({"detail":"DATA_INSUFFICIENT"}, status=status.HTTP_400_BAD_REQUEST)
            
            
            
            
            
            
            
            for field,value in message_data.items():
                field = str(field)
                
                if field == "email":
                    email_data = value
                    
                    # Email Definition
                    definition_dict = {
                                        "sender_role": role_query.pk,
                                        "sender_name": email_data.get("from_name"),
                                        "sender_address": user_query.primary_email,
                                        "subject": email_data.get("subject"),
                                        "body": email_data.get("body"),
                                        "html": email_data.get("html"),
                                      }
                
                    # Email Messages
                    # Currently supports users only
                    supplied_recipients = list(email_data.get("recipients"))
                
                    # Send the thing
                    email_status = send_email(definition_dict,supplied_recipients)
                    
                    return_message = {message_nonce: email_status.get("message")}
                    
                    if email_status.get("success"):
                        completed_messages.update(return_message)
                    else:
                        failed_messages.update(return_message)
                    
                    
                elif field == "sms":
                    failed_messages.update({message_nonce: "MESSAGE_TYPE_UNSUPPORTED"})
                    skip_message = True
                    break
                else:
                    failed_messages.update({message_nonce: "FIELD_IDENTIFIER_INVALID"})
                    skip_message = True
                    break
            
            if skip_message:
                continue
                
        return Response({
            "fail": {
                "nonce": failed_messages
            },
            "success": {
                "nonce_id": completed_messages
            }
        })