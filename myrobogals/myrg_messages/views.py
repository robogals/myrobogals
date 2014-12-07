from __future__ import unicode_literals
from future.builtins import *
import six


from myrg_core.classes import RobogalsAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from django.db.models import Q
from django.utils import timezone

from .functions import send_email
from .serializers import EmailDefinitionSerializer, EmailMessageSerializer



MAX_MESSAGES = 1

PAGINATION_MAX_LENGTH = 1000





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
            
            
            
            
            
            
            
            for field,value in six.iteritems(message_data):
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

                    merge_tags = email_data.get("merge_tags")
                
                    #import pdb; pdb.set_trace()
                    # Send the thing
                    email_status = send_email(definition_dict,supplied_recipients,merge_tags)
                    
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

class ListEmailDefinition(RobogalsAPIView):
    def post(self, request, format=None):
        try:
            requested_fields = list(request.DATA.get("query"))
            requested_pagination = dict(request.DATA.get("pagination"))
        except:
            return Response({"detail":"DATA_FORMAT_INVALID"}, status=status.HTTP_400_BAD_REQUEST)
            
        if (not requested_fields) or (not requested_pagination):
            return Response({"detail":"DATA_INSUFFICIENT"}, status=status.HTTP_400_BAD_REQUEST)
        
        
        # Pagination
        pagination_page_index = requested_pagination.get("page")
        pagination_page_length = requested_pagination.get("length")
        
        if (pagination_page_index is None) or (pagination_page_length is None):
            return Response({"detail":"DATA_INSUFFICIENT"}, status=status.HTTP_400_BAD_REQUEST)
        
        pagination_page_index = int(pagination_page_index)
        pagination_page_length = int(pagination_page_length)
        
        pagination_start_index = pagination_page_index * pagination_page_length
        pagination_end_index = pagination_start_index + (pagination_page_length if pagination_page_length < PAGINATION_MAX_LENGTH else PAGINATION_MAX_LENGTH)
            
        if pagination_start_index < 0 or pagination_end_index < 0:
            return Response({"detail":"PAGINATION_NEGATIVE_INDEX_UNSUPPORTED"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = EmailDefinitionSerializer
        
        # Filter
        filter_dict = {}
        sort_fields = []
        fields = ["id"]
        
        for field_object in requested_fields:
            field_name = field_object.get("field")
            field_query = field_object.get("search")
            field_order = field_object.get("order")
            field_visibility = field_object.get("visibility")
            
            if (field_name is None):
                return Response({"detail":"FIELD_IDENTIFIER_MISSING"}, status=status.HTTP_400_BAD_REQUEST)
            
            field_name = str(field_name)
            
            # Block protected fields like passwords
            if field_name in serializer.Meta.model.PROTECTED_FIELDS:
                return Response({"detail":"`{}` is a protected field.".format(field_name)}, status=status.HTTP_400_BAD_REQUEST)
            
            # Non-valid field names
            # ! Uses _meta non-documented API
            try:
                serializer.Meta.model._meta.get_field_by_name(field_name)
            except FieldDoesNotExist:
                return Response({"detail":"`{}` is not a valid field name.".format(field_name)}, status=status.HTTP_400_BAD_REQUEST)
                
            if (field_query is not None):
                filter_dict.update({field_name+"__icontains": str(field_query)})
            
            if (field_order is not None):
                field_order = str(field_order)
                
                if field_order == "a":
                    sort_fields.append(field_name)
                if field_order == "d":
                    sort_fields.append("-"+field_name)
            
            if not (field_visibility == False):
                fields.append(field_name)
        
        
        # Build query
        query = serializer.Meta.model.objects.filter(**filter_dict)
        query = query.order_by(*sort_fields)
        
        query_size = query.count()
        
        query = query[pagination_start_index:pagination_end_index]
        
        
        #import pdb; pdb.set_trace()
        # Serialize
        serialized_query = serializer(query, many=True, fields=fields)
        
        
        # Output
        output_list = []
        
        for emailDefinition_object in serialized_query.data:
            new_dict = {}
            new_dict.update({"id": emailDefinition_object.pop("id")})
            new_dict.update({"data": emailDefinition_object})
        
            output_list.append(new_dict)
        
        
        return Response({
                            "meta": {
                                "size": query_size
                            },
                            "emailDefinition": output_list
                        })

class ListEmailMessage(RobogalsAPIView):
    def post(self, request, format=None):
        try:
            requested_fields = list(request.DATA.get("query"))
            requested_pagination = dict(request.DATA.get("pagination"))
        except:
            return Response({"detail":"DATA_FORMAT_INVALID"}, status=status.HTTP_400_BAD_REQUEST)
            
        if (not requested_fields) or (not requested_pagination):
            return Response({"detail":"DATA_INSUFFICIENT"}, status=status.HTTP_400_BAD_REQUEST)
        
        
        # Pagination
        pagination_page_index = requested_pagination.get("page")
        pagination_page_length = requested_pagination.get("length")
        
        if (pagination_page_index is None) or (pagination_page_length is None):
            return Response({"detail":"DATA_INSUFFICIENT"}, status=status.HTTP_400_BAD_REQUEST)
        
        pagination_page_index = int(pagination_page_index)
        pagination_page_length = int(pagination_page_length)
        
        pagination_start_index = pagination_page_index * pagination_page_length
        pagination_end_index = pagination_start_index + (pagination_page_length if pagination_page_length < PAGINATION_MAX_LENGTH else PAGINATION_MAX_LENGTH)
            
        if pagination_start_index < 0 or pagination_end_index < 0:
            return Response({"detail":"PAGINATION_NEGATIVE_INDEX_UNSUPPORTED"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = EmailMessageSerializer
        
        # Filter
        filter_dict = {}
        sort_fields = []
        fields = ["id"]
        
        for field_object in requested_fields:
            field_name = field_object.get("field")
            field_query = field_object.get("search")
            field_order = field_object.get("order")
            field_visibility = field_object.get("visibility")
            
            if (field_name is None):
                return Response({"detail":"FIELD_IDENTIFIER_MISSING"}, status=status.HTTP_400_BAD_REQUEST)
            
            field_name = str(field_name)
            
            # Block protected fields like passwords
            if field_name in serializer.Meta.model.PROTECTED_FIELDS:
                return Response({"detail":"`{}` is a protected field.".format(field_name)}, status=status.HTTP_400_BAD_REQUEST)
            
            #import pdb; pdb.set_trace()
            # Non-valid field names
            # ! Uses _meta non-documented API
            try:
                field_object, model, direct, m2m = serializer.Meta.model._meta.get_field_by_name(field_name)
            except FieldDoesNotExist:
                return Response({"detail":"`{}` is not a valid field name.".format(field_name)}, status=status.HTTP_400_BAD_REQUEST)
                
            if (field_query is not None):
                if (isinstance(field_object, django.db.models.fields.related.ForeignKey)):
                    filter_dict.update({field_name+"__id": str(field_query)})
                else:
                    filter_dict.update({field_name+"__icontains": str(field_query)})
            
            if (field_order is not None):
                field_order = str(field_order)
                
                if field_order == "a":
                    sort_fields.append(field_name)
                if field_order == "d":
                    sort_fields.append("-"+field_name)
            
            if not (field_visibility == False):
                fields.append(field_name)
        
        
        #import pdb; pdb.set_trace()
        # Build query
        try:
            query = serializer.Meta.model.objects.filter(**filter_dict)
        except Exception as e:
            return Response({"detail":"DATA_FORMAT_INVALID"}, status=status.HTTP_400_BAD_REQUEST)

        query = query.order_by(*sort_fields)
        
        query_size = query.count()
        
        query = query[pagination_start_index:pagination_end_index]
        
        
        #import pdb; pdb.set_trace()
        # Serialize
        serialized_query = serializer(query, many=True, fields=fields)
        
        
        # Output
        output_list = []
        
        for emailMessage_object in serialized_query.data:
            new_dict = {}
            new_dict.update({"id": emailMessage_object.pop("id")})
            new_dict.update({"data": emailMessage_object})
        
            output_list.append(new_dict)
        
        
        return Response({
                            "meta": {
                                "size": query_size
                            },
                            "emailMessage": output_list
                        })

