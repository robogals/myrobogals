from __future__ import unicode_literals
from future.builtins import *
import six
from django.utils.encoding import smart_text


from myrg_core.classes import RobogalsAPIView
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import status

from django.db.models.fields import FieldDoesNotExist
from django.db.models import Q
from django.db import transaction
from django.utils import timezone

from .models import RepoContainer, RepoFile
from .serializers import RepoContainerSerializer, RepoFileSerializer
from .forms import UploadFileForm

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse

from myrg_permissions.custom_permissions import AnyPermissions, PermissionManager
from rest_framework import permissions
from django.shortcuts import get_object_or_404

import json
# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

PAGINATION_MAX_LENGTH = 1000

MAX_REPOS = 1
        
# Repo Container
################################################################################
class ListRepoContainers(RobogalsAPIView):
    def post(self, request, format=None):
        ################################################################
        # Permission restricted viewing to be implemented here
        #
        # format -> PermissionManager.permission_checked("id","name of permission", "user", "model")
        # This permission can be combined with other type of permission with operator "or" or "and"
        permited = PermissionManager.permission_checked(None, "REPOSITORY_SELF_VIEW",request.user, None) and PermissionManager.permission_checked(None, "REPOSITORY_PUBLIC_VIEW",request.user, None) or True 
        # note: delete this "or True" to disable public permission to view repocontainer
        
        if not permited:
            logger.error("permission denied")
            return Response({"PERMISSION_DENIED"}, status=status.HTTP_403_BAD_REQUEST)
        ################################################################
        from myrg_users.serializers import RobogalsUserSerializer
        from myrg_users.models import RobogalsUser

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
        key_title = "~"
        key_tags = "~"
        filter_dict = {} 
        sort_fields = []
        fields = ["id", "user", "role"] 
        
        for field_object in requested_fields:
            field_name = field_object.get("field")
            field_query = field_object.get("search")
            field_order = field_object.get("order") 
            field_visibility = field_object.get("visibility")  
            
            if (field_name is None):
                return Response({"detail":"FIELD_IDENTIFIER_MISSING"}, status=status.HTTP_400_BAD_REQUEST)
            
            field_name = str(field_name)
            
            # Block protected fields 
            if field_name in RepoContainer.PROTECTED_FIELDS:
                return Response({"detail":"`{}` is a protected field.".format(field_name)}, status=status.HTTP_400_BAD_REQUEST)
            
            # Non-valid field names
            # ! Uses _meta non-documented API
            try:
                RepoContainer._meta.get_field_by_name(field_name)
            except FieldDoesNotExist:
                return Response({"detail":"`{}` is not a valid field name.".format(field_name)}, status=status.HTTP_400_BAD_REQUEST)
                
            if (field_query is not None):
                if (field_name == "title" and field_query != ""):
                    key_title = str(field_query)
                elif (field_name == "tags" and field_query != ""):
                    key_tags = str(field_query )
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
        
        
        # Build query
        query = RepoContainer.objects.filter(service__gt=0)
        if (key_title == "~" and key_tags == "~" ):
            query = query.filter(**filter_dict)
        else:
            query = query.filter(Q(title__icontains=key_title) | Q(tags__icontains=key_tags))
        query = query.order_by(*sort_fields)
        
            
        query_size = query.count()
        
        query = query[pagination_start_index:pagination_end_index]
        
        
        # Serialize
        serializer = RepoContainerSerializer
        serializer.Meta.fields = fields
        
        serialized_query = serializer(query, many=True)
        
        # Output
        output_list = [] 
        
        for repocontainer_object in serialized_query.data:
            new_dict = {}
            new_dict.update({"id": repocontainer_object.pop("id")})
            new_dict.update({"data": repocontainer_object})
            # checked user property and retrieve information for user(from user model) 
            # http://stackoverflow.com/questions/11748234/
            if repocontainer_object.get('user'):
                user_id = repocontainer_object.pop("user")
                user = RobogalsUser.objects.filter(id = user_id)
                user_serializer = RobogalsUserSerializer
                user_serializer.Meta.fields = ("given_name",)
                user_serializer_query = user_serializer(user, many=True)
                user_data = user_serializer_query.data
                new_dict.update({"user": user_data})
        
            output_list.append(new_dict)   
        
        
        return Response({ 
                            "meta": {
                                "size": query_size
                            }, 
                            "rcl": output_list
                        })

class DeleteRepoContainers(RobogalsAPIView):
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
        commit = ""
        
        for idx,pk in enumerate(requested_ids):
            if not isinstance(pk, six.string_types):
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
            ################################################################
            # Permission restricted viewing to be implemented here
            #
            # format -> PermissionManager.permission_checked("id","name of permission", "user", "model")
            permited = PermissionManager.permission_checked(pk,"REPOSITORY_SELF_DELETE",request.user, RepoContainer)
            if not permited:
               return Response({"PERMISSION_DENIED"}, status=status.HTTP_403_FORBIDDEN)
                   
            ################################################################
        
        # Remove bad IDs
        requested_ids = [pk for idx,pk in enumerate(requested_ids) if idx not in ids_to_remove]
        
        # Run query
        try:
            with transaction.atomic():
                query = RepoContainer.objects.filter(service__gt=0, id__in=requested_ids)
                affected_ids = [obj.get("id") for obj in query.values("id")]
                affected_num_rows = query.update(service=0)
        except:
            for pk in requested_ids:
                failed_ids.update({pk: "OBJECT_NOT_MODIFIED"})

        # Gather up non-deleted IDs
        non_deleted_ids = list(set(requested_ids)-set(affected_ids))
        
        for pk in non_deleted_ids:
            failed_ids.update({pk: "OBJECT_NOT_MODIFIED"})
        
        if failed_ids == {}:
            commit = "true"
        else:
            commit = "false"
        
        return Response({
            "fail": {
                "id": failed_ids,
            },
            "success": {
                "id": affected_ids
            },
            "commit": commit
        })
        
class EditRepoContainers(RobogalsAPIView):
    def post(self, request, format=None):
        # request.DATA
        try:
            supplied_repocontaineres = list(request.DATA.get("rc"))
        except:
            return Response({"detail":"DATA_FORMAT_INVALID"}, status=status.HTTP_400_BAD_REQUEST)
                
        failed_repocontainer_updates = {}
        completed_repocontainer_updates = []
        
        # Filter out bad data
        for repocontainer_object in supplied_repocontaineres:
            skip_repocontainer = False
            repocontainer_update_dict = {}
            
            
            try:
                repocontainer_id = smart_text(repocontainer_object.get("id"))
                repocontainer_data = dict(repocontainer_object.get("data"))
            except:
                return Response({"detail":"DATA_FORMAT_INVALID"}, status=status.HTTP_400_BAD_REQUEST)
            
            if (repocontainer_id is None):
                return Response({"detail":"DATA_INSUFFICIENT"}, status=status.HTTP_400_BAD_REQUEST)
            
            for field,value in six.iteritems(repocontainer_data):
                field = str(field)
                
                # Read only fields
                if field in RepoContainer.READONLY_FIELDS:
                    failed_repocontainer_updates.update({repocontainer_id: "FIELD_READ_ONLY"})
                    skip_repocontainer = True
                    break
                
                # Non-valid field names
                # ! Uses _meta non-documented API
                try:
                    RepoContainer._meta.get_field_by_name(field)
                except FieldDoesNotExist:
                    failed_repocontainer_updates.update({repocontainer_id: "FIELD_IDENTIFIER_INVALID"})
                    skip_repocontainer = True
                    break
                    
                ################################################################
                # Permission restricted viewing to be implemented here
                #
                # format -> PermissionManager.permission_checked("id","name of permission", "user", "model")
                permited = PermissionManager.permission_checked(repocontainer_id,"REPOSITORY_SELF_EDIT",request.user, RepoContainer)
                if not permited:
                   #logger.error("permission denied")
                   #failed_repocontainer_updates.update({repocontainer_id: "PERMISSION_DENIED"})
                   #skip_repocontainer = True
                   #break
                   return Response({"PERMISSION_DENIED"}, status=status.HTTP_403_FORBIDDEN)
                   
                ################################################################
            
                # Add to update data dict
                repocontainer_update_dict.update({field: value})
            
            if skip_repocontainer:
                continue
            
                
            
            # Fetch, serialise and save
            try:
                repocontainer_query = RepoContainer.objects.get(pk=repocontainer_id)
            except:
                failed_repocontainer_updates.update({repocontainer_id: "OBJECT_NOT_FOUND"})
                continue
                
            serializer = RepoContainerSerializer
            serialized_repocontainer = serializer(repocontainer_query, data=repocontainer_update_dict, partial=True)
        
            if serialized_repocontainer.is_valid():
                try:
                    with transaction.atomic():
                        serialized_repocontainer.save()
                        completed_repocontainer_updates.append(repocontainer_id)
                except:
                    failed_repocontainer_updates.update({repocontainer_id: "OBJECT_NOT_MODIFIED"})
            else:
                failed_repocontainer_updates.update({repocontainer_id: "DATA_VALIDATION_FAILED"})
                
        return Response({
            "fail": {
                "id": failed_repocontainer_updates
            },
            "success": {
                "id": completed_repocontainer_updates
            },
            "commit": serialized_repocontainer.is_valid()
        })

class CreateRepoContainers(RobogalsAPIView):
    def post(self, request, format=None):
        try:
            supplied_repocontainers = list(request.DATA.get("rc"))
        except:
            return Response({"detail":"DATA_FORMAT_INVALID"}, status=status.HTTP_400_BAD_REQUEST)
                
        if len(supplied_repocontainers) > MAX_REPOS:
            return Response({"detail":"REQUEST_OVER_OBJECT_LIMIT"}, status=status.HTTP_400_BAD_REQUEST)
        
        failed_repocontainer_creations = {}
        completed_repocontainer_creations = {}
        
        # Filter out bad data
        for repocontainer_object in supplied_repocontainers:
            skip_repocontainer = False
            repocontainer_create_dict = {}
            
            try:  
                repocontainer_nonce = repocontainer_object.get("nonce")
                repocontainer_data = dict(repocontainer_object.get("data"))
            except:
                return Response({"detail":"DATA_FORMAT_INVALID"}, status=status.HTTP_400_BAD_REQUEST)
            
            if (repocontainer_nonce is None):
                return Response({"detail":"DATA_INSUFFICIENT"}, status=status.HTTP_400_BAD_REQUEST)
            
            for field,value in six.iteritems(repocontainer_data):
                field = str(field)
                
                # Read only fields
                if field in RepoContainer.READONLY_FIELDS:
                    failed_repocontainer_creations.update({repocontainer_nonce: "FIELD_READ_ONLY"})
                    skip_repocontainer = True
                    break
                
                # Non-valid field names
                # ! Uses _meta non-documented API
                try:
                    RepoContainer._meta.get_field_by_name(field)
                except FieldDoesNotExist:
                    failed_repocontainer_creations.update({repocontainer_nonce: "FIELD_IDENTIFIER_INVALID"})
                    skip_repocontainer = True
                    break
            
            
                # Add to update data dict
                repocontainer_create_dict.update({field: value})
            
            if skip_repocontainer: 
                continue  
            
            # Serialise and save
            serializer = RepoContainerSerializer
            serialized_repocontainer = serializer(data=repocontainer_create_dict)
            
            if serialized_repocontainer.is_valid():
                try:
                    with transaction.atomic():
                         repocontainer = serialized_repocontainer.save()
                         completed_repocontainer_creations.update({repocontainer_nonce: repocontainer.id})
                except:
                    failed_repocontainer_creations.update({repocontainer_nonce: "OBJECT_NOT_MODIFIED"})
            else:
                failed_repocontainer_creations.update({repocontainer_nonce: "DATA_VALIDATION_FAILED"})
                
        return Response({
            "fail": {
                "nonce": serialized_repocontainer.errors #repocontainer_create_dict#failed_repocontainer_creations
            },
            "success": {
                "nonce_id": completed_repocontainer_creations
            },
            "commit": serialized_repocontainer.is_valid()  
        })
        
        
# RepoFile
################################################################################
class ListRepoFiles(RobogalsAPIView):
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
            field_query = field_object.get("search")
            field_order = field_object.get("order")
            field_visibility = field_object.get("visibility")
            
            if (field_name is None):
                return Response({"detail":"FIELD_IDENTIFIER_MISSING"}, status=status.HTTP_400_BAD_REQUEST)
            
            field_name = str(field_name)
             
            # Block protected fields like passwords
            if field_name in RepoFile.PROTECTED_FIELDS:
                return Response({"detail":"`{}` is a protected field.".format(field_name)}, status=status.HTTP_400_BAD_REQUEST)
            
            # Non-valid field names
            # ! Uses _meta non-documented API 
            try:
                RepoFile._meta.get_field_by_name(field_name)
            except FieldDoesNotExist:
                return Response({"detail":"`{}` is not a valid field name.".format(field_name)}, status=status.HTTP_400_BAD_REQUEST)
                
            if (field_query is not None and field_name == "container"):
                filter_dict.update({field_name+"__id__icontains": str(field_query)})
            elif (field_query is not None):
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
        query = RepoFile.objects.all()
        query = query.filter(**filter_dict)
        query = query.order_by(*sort_fields)
        
        query_size = query.count()
        
        query = query[pagination_start_index:pagination_end_index]
        
        
        # Serialize
        serializer = RepoFileSerializer
        serializer.Meta.fields = fields
        
        serialized_query = serializer(query, many=True)
        
          
        # Output
        output_list = []
        
        for repofile_object in serialized_query.data:
            new_dict = {}
            new_dict.update({"id": repofile_object.pop("id")})
            new_dict.update({"data": repofile_object})
        
            output_list.append(new_dict)
        
        
        return Response({
                            "meta": {
                                "size": query_size
                            },
                            "rfl": output_list
                        })

class DeleteRepoFiles(RobogalsAPIView):
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
                    
            ################################################################
            # Permission restricted viewing to be implemented here
            #
            #get repocontainer_id based on repofile_id
            rc_id = RepoFile.objects.filter(id=pk)
            # format -> PermissionManager.permission_checked("id","name of permission", "user", "model")
            permited = PermissionManager.permission_checked(rc_id[0].container_id,"REPOSITORY_SELF_DELETE",request.user, RepoContainer)
            if not permited:
               return Response({"PERMISSION_DENIED"}, status=status.HTTP_403_FORBIDDEN)
                   
            ################################################################
        
        # Remove bad IDs
        requested_ids = [pk for idx,pk in enumerate(requested_ids) if idx not in ids_to_remove]
        
        # Run query
        try:
            with transaction.atomic():
                query = RepoFile.objects.filter(id__in=requested_ids)
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
        
def upload(request):
        # Handle file upload
        if request.method == 'POST':
            form = UploadFileForm(request.POST, request.FILES)
            repocontainer=RepoContainer.objects.get(id=request.POST['container'])
            if form.is_valid():
                uploadfile = RepoFile.objects.create(name = request.POST['name'], 
                                                 file = request.FILES['file'], 
                                                 container = repocontainer
                                                 )
                uploadfile.save()
                status = "200"
        else:
            form = UploadFileForm() # A empty, unbound form
            status = "500"
            

        # Render list page with the uploadfiles and the form --> page for testing purpose
        return render_to_response(
             'upload.html',
             {'response': status})
        
# Receive the pre_delete signal and delete the file associated with the model instance.
from django.db.models.signals import post_delete
from django.dispatch.dispatcher import receiver

@receiver(post_delete, sender=RepoFile)
def repofile_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    instance.file.delete(False)
