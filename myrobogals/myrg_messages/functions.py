from __future__ import unicode_literals
from future.builtins import *
import six



from django.db.models.fields import FieldDoesNotExist
from django.db import transaction
from django.template.loader import render_to_string

from myrg_users.models import RobogalsUser

from django.conf import settings

from .models import EmailDefinition, EmailMessage
from .serializers import EmailDefinitionSerializer

from collections import OrderedDict

import mandrill

def send_email(definition_dict,supplied_recipients,merge_tags,template_dict = None):
    def return_status(success,message):
        return { "success": success, "message": message }
    
    definition_dict_internal = definition_dict
    
    message_dict = {
                    'auto_html': False,
                    'auto_text': True,
                    
                    'from_email': None,
                    'from_name': None,
                    
                    'to': [],
                    'subject': None,
                    
                    'text': None,
                    'html': None,
                    'inline_css': True,
                    
                    'preserve_recipients': False,           # Like BCC, but generates [many email] -> [many TO], rather than [one email] -> [many BCC]
                    
                    'track_clicks': True,
                    'track_opens': True,
                    #'global_merge_vars': merge_tags["global_merge_vars"]
                   }
        
    if template_dict:
        template = template_dict.get("template")
        title = template_dict.get("title")
        body = definition_dict_internal.get("body")
        
        try:
            definition_dict_internal['body'] = render_to_string(template, {
                                                                    'title': title,
                                                                    'body': body,
                                                                 })
        except:
                return return_status(False,"MESSAGE_GENERATION_FAILED")
    
    # Email Definition
    # definition_dict = {
                        # "sender_role": role_query.pk,
                        # "sender_name": email_data.get("from_name"),
                        # "sender_address": user_query.primary_email,
                        # "subject": email_data.get("subject"),
                        # "body": email_data.get("body"),
                        # "html": email_data.get("html"),
                      # }

    serializer = EmailDefinitionSerializer
    serialized_message_def = serializer(data=definition_dict_internal)
    
    #import pdb; pdb.set_trace()
    if not serialized_message_def.is_valid():
        return return_status(False,"DATA_VALIDATION_FAILED")



    # Email Messages
    # Currently supports users only
    #supplied_recipients = list(email_data.get("recipients"))
    user_list = []
    recipients_list = []
    email_user_dict = {}
        
    for recipient_object in supplied_recipients:
        for field2,value2 in six.iteritems(recipient_object):
            field2 = str(field2)
            
            if field2 == "user":
                user_list.append(str(value2))
            else:
                return return_status(False,"FIELD_IDENTIFIER_INVALID")

    #import pdb; pdb.set_trace()
    # Remove duplicates
    user_list = list(OrderedDict.fromkeys(user_list))
                        
    user_query = RobogalsUser.objects.filter(is_active=True, pk__in=user_list)
    
    # merge_vars = []
    for user in user_query:
        email_user_dict.update({user.primary_email: user})
        
        recipients_list.append({
                                    "email": user.primary_email,
                                    "name": user.get_preferred_name(),
                                    "type": "to",
                                })
        # merge_vars.append({
                            # 'rcpt': user.primary_email,
                            # 'vars': merge_tags["merge_vars"][user.pk]
                          # })
        user_list.remove(user.pk)
        # del merge_tags["merge_vars"][user.pk]
    
    # If there are users not in the returned query
    #if len(user_list) > 0 or len(merge_tags["merge_vars"]) > 0:
    if len(user_list) > 0:
        return return_status(False,"OBJECT_NOT_FOUND")
    
    
    
    
    # Finish message
    message_dict.update({
                            "to": recipients_list,
                            "subject": definition_dict_internal.get("subject"),
                            "from_name": definition_dict_internal.get("sender_name"),
                            "from_email": definition_dict_internal.get("sender_address"),
                            # "merge_vars": merge_vars
                        })
    
    if definition_dict_internal.get("html"):
        message_dict.update({"html": definition_dict_internal.get("body")})
    else:
        message_dict.update({"text": definition_dict_internal.get("body")})

    
    #import pdb; pdb.set_trace()
    # Send
    try:
        with transaction.atomic():
            message_def = serialized_message_def.save()
            
            mandrill_client = mandrill.Mandrill(settings.MANDRILL_API_KEY)
            mandrill_result = mandrill_client.messages.send(message=message_dict, async=False)
    except Exception as e:
        return return_status(False,"MESSAGE_DELIVERY_FAILED")
        

    message_marker_list = []
    
    for message in mandrill_result:
        message_marker_dict = {
                                "definition" : message_def,
                                "recipient_user" : email_user_dict.get(message.get("email")),
                                "recipient_name" : email_user_dict.get(message.get("email")).get_preferred_name(),
                                "recipient_address" : message.get("email"),
                                "service_id" : message.get("_id"),
                                "service_status" : message.get("status"),
                              }
        message_marker_list.append(EmailMessage(**message_marker_dict))

    
    try:
        with transaction.atomic():
            EmailMessage.objects.bulk_create(message_marker_list)      
    except:
        return return_status(False,"MESSAGE_MARKER_SAVE_FAILED")

    return return_status(True,message_def.pk)
