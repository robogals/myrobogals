from __future__ import unicode_literals
from future.builtins import *
import six
from django.utils.encoding import smart_text


from myrg_core.classes import RobogalsAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import status

from django.db.models.fields import FieldDoesNotExist
from django.db.models import Q
from django.db import transaction
from django.utils import timezone

from .models import PermissionList
from .serializers import PermissionListSerializer

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse

from myrg_permissions.custom_permissions import AnyPermissions, IsAdminRobogals, IsTeamMember, IsPublicUser
from rest_framework import permissions
from django.shortcuts import get_object_or_404

# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

PAGINATION_MAX_LENGTH = 1000

MAX_REPOS = 1
        
# Permissions
################################################################################
class ListPermission(RobogalsAPIView):
    def post(self, request, format=None):
        # request.DATA
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
        
         
        # Filter
        filter_dict = {}
        sort_fields = []
        fields = ["id"]  
        
        for field_object in requested_fields:
            field_name = field_object.get("field")
            field_query = field_object.get("seapermissionh")
            field_order = field_object.get("order")
            field_visibility = field_object.get("visibility")
            
            if (field_name is None):
                return Response({"detail":"FIELD_IDENTIFIER_MISSING"}, status=status.HTTP_400_BAD_REQUEST)
            
            field_name = str(field_name)
             
            # Non-valid field names
            # ! Uses _meta non-documented API 
            try:
                PermissionList._meta.get_field_by_name(field_name)
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
        query = PermissionList.objects.all()
        query = query.filter(**filter_dict)
        query = query.order_by(*sort_fields)
        
        query_size = query.count()
        
        query = query[pagination_start_index:pagination_end_index]
        
        
        # Serialize
        serializer = PermissionListSerializer
        serializer.Meta.fields = fields
        
        serialized_query = serializer(query, many=True)
        
          
        # Output
        output_list = []
        
        for permissionlist_object in serialized_query.data:
            new_dict = {}
            new_dict.update({"id": permissionlist_object.pop("id")})
            new_dict.update({"data": permissionlist_object})
        
            output_list.append(new_dict)
        
        
        return Response({
                            "meta": {
                                "size": query_size
                            },
                            "permissions": output_list
                        })

class DeletePermissionLists(RobogalsAPIView):
    def post(self, request, format=None):
        # request.DATA
        try:
            requested_ids = list(set(request.DATA.get("id")))
        except:
            return Response({"detail":"DATA_FORMAT_INVALID"}, status=status.HTTP_400_BAD_REQUEST)
        
        if (not requested_ids):
            return Response({"detail":"DATA_INSUFFICIENT"}, status=status.HTTP_400_BAD_REQUEST)
        
        
        # Filter out bad IDs 
        ids_to_remove = []
        failed_ids = {}
        affected_ids = []
        
        for idx,pk in enumerate(requested_ids):
            if not isinstance(pk, int):
                ids_to_remove.append(idx)
                failed_ids.update({pk: "DATA_FORMAT_INVALID"})
                continue
                    
            ####################################################################
            # Permission restricted deletion to be implemented here
            #
            # if not permission_allows_deletion_of_this_id:
            #   ids_to_remove.append(idx)
            #   failed_ids.update({pk: "PERMISSION_DENIED"})
            ####################################################################
        
        # Remove bad IDs
        requested_ids = [pk for idx,pk in enumerate(requested_ids) if idx not in ids_to_remove]
        
        # Run query
        try:
            with transaction.atomic():
                query = PermissionList.objects.filter(id__in=requested_ids)
                affected_ids = [obj.get("id") for obj in query.values("id")]
                affected_num_rows = query.delete()
        except:
            for pk in requested_ids:
                failed_ids.update({pk: "OBJECT_NOT_MODIFIED"})

        # Gather up non-deleted IDs
        non_deleted_ids = list(set(requested_ids)-set(affected_ids))
        
        for pk in non_deleted_ids:
            failed_ids.update({pk: "OBJECT_NOT_MODIFIED"})
        
        
        
        return Response({
            "fail": {
                "id": failed_ids,
            },
            "success": {
                "id": affected_ids
            }
        })
        
class EditPermissionLists(RobogalsAPIView):
    def post(self, request, format=None):
        # request.DATA
        try:
            supplied_permissionlists = list(request.DATA.get("permission"))
        except:
            return Response({"detail":"DATA_FORMAT_INVALID"}, status=status.HTTP_400_BAD_REQUEST)
                
        failed_permissionlist_updates = {}
        completed_permissionlist_updates = []
        
        # Filter out bad data
        for permissionlist_object in supplied_permissionlists:
            skip_permissionlist = False
            permissionlist_update_dict = {}
            
            
            try:
                permissionlist_id = smart_text(permissionlist_object.get("id"))
                permissionlist_data = dict(permissionlist_object.get("data"))
            except:
                return Response({"detail":"DATA_FORMAT_INVALID"}, status=status.HTTP_400_BAD_REQUEST)
            
            if (permissionlist_id is None):
                return Response({"detail":"DATA_INSUFFICIENT"}, status=status.HTTP_400_BAD_REQUEST)
            
            for field,value in six.iteritems(permissionlist_data):
                field = str(field)
                
                # Read only fields
                if field in PermissionList.READONLY_FIELDS:
                    failed_permissionlist_updates.update({permissionlist_id: "FIELD_READ_ONLY"})
                    skip_permissionlist = True
                    break
                
                # Non-valid field names
                # ! Uses _meta non-documented API
                try:
                    PermissionList._meta.get_field_by_name(field)
                except FieldDoesNotExist:
                    failed_permissionlist_updates.update({permissionlist_id: "FIELD_IDENTIFIER_INVALID"})
                    skip_permissionlist = True
                    break
                    
                ################################################################
                # Permission restricted editing to be implemented here
                #
                # if not permission_allows_editing_of_this_id:
                #   failed_permissionlist_updates.update({pk: "PERMISSION_DENIED"})
                #   skip_roleclass = True
                #   break
                ################################################################
            
                # Add to update data dict
                permissionlist_update_dict.update({field: value})
            
            if skip_permissionlist:
                continue
            
            
            # Fetch, serialise and save
            try:
                permissionlist_query = PermissionList.objects.get(pk=permissionlist_id)
            except:
                failed_permissionlist_updates.update({permissionlist_id: "OBJECT_NOT_FOUND"})
                continue
                
            serializer = PermissionListSerializer
            serialized_permissionlist = serializer(permissionlist_query, data=permissionlist_update_dict, partial=True)
        
            if serialized_permissionlist.is_valid():
                try:
                    with transaction.atomic():
                        serialized_permissionlist.save()
                        completed_permissionlist_updates.append(permissionlist_id)
                except:
                    failed_permissionlist_updates.update({permissionlist_id: "OBJECT_NOT_MODIFIED"})
            else:
                failed_permissionlist_updates.update({permissionlist_id: "DATA_VALIDATION_FAILED"})
                
        return Response({
            "fail": {
                "id": failed_permissionlist_updates
            },
            "success": {
                "id": completed_permissionlist_updates
            },
            "commit": serialized_permissionlist.is_valid()
        })

class CreatePermissionLists(RobogalsAPIView):
    permission_classes = [AnyPermissions]
    any_permission_classes = [IsAdminRobogals, IsPublicUser]
    def post(self, request, format=None):
        loggers.error(self)
        loggers.error(request)
        # request.DATA
        try:
            supplied_permissionlists = list(request.DATA.get("permission"))
        except:
            return Response({"detail":"DATA_FORMAT_INVALID"}, status=status.HTTP_400_BAD_REQUEST)
                
        if len(supplied_permissionlists) > MAX_REPOS:
            return Response({"detail":"REQUEST_OVER_OBJECT_LIMIT"}, status=status.HTTP_400_BAD_REQUEST)
        
        failed_permissionlist_creations = {}
        completed_permissionlist_creations = {}
        
        # Filter out bad data
        for permissionlist_object in supplied_permissionlists:
            skip_permissionlist = False
            permissionlist_create_dict = {}
            
            try:  
                permissionlist_nonce = permissionlist_object.get("nonce")
                permissionlist_data = dict(permissionlist_object.get("data"))
            except:
                return Response({"detail":"DATA_FORMAT_INVALID"}, status=status.HTTP_400_BAD_REQUEST)
            
            if (permissionlist_nonce is None):
                return Response({"detail":"DATA_INSUFFICIENT"}, status=status.HTTP_400_BAD_REQUEST)
            
            for field,value in six.iteritems(permissionlist_data):
                field = str(field)
                
                # Read only fields
                if field in PermissionList.READONLY_FIELDS:
                    failed_permissionlist_creations.update({permissionlist_nonce: "FIELD_READ_ONLY"})
                    skip_permissionlist = True
                    break
                
                # Non-valid field names
                # ! Uses _meta non-documented API
                try:
                    PermissionList._meta.get_field_by_name(field)
                except FieldDoesNotExist:
                    failed_permissionlist_creations.update({permissionlist_nonce: "FIELD_IDENTIFIER_INVALID"})
                    skip_permissionlist = True
                    break
            
            
                # Add to update data dict
                permissionlist_create_dict.update({field: value})
            
            if skip_permissionlist: 
                continue  
            
            # Serialise and save
            serializer = PermissionListSerializer
            serialized_permissionlist = serializer(data=permissionlist_create_dict)
            
            if serialized_permissionlist.is_valid():
                try:
                    with transaction.atomic():
                         permissionlist = serialized_permissionlist.save()
                         completed_permissionlist_creations.update({permissionlist_nonce: permissionlist.id})
                except:
                    failed_permissionlist_creations.update({permissionlist_nonce: "OBJECT_NOT_MODIFIED"})
            else:
                failed_permissionlist_creations.update({permissionlist_nonce: "DATA_VALIDATION_FAILED"})
                
        return Response({
            "fail": {
                "nonce": serialized_permissionlist.errors #permissionlist_create_dict#failed_permissionlist_creations
            },
            "success": {
                "nonce_id": completed_permissionlist_creations
            },
            "commit": serialized_permissionlist.is_valid()  
        })
        
        
