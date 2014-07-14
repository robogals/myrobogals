from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from django.db.models.fields import FieldDoesNotExist
from django.db.models import Q
from django.db import transaction
from django.utils import timezone

from .models import RobogalsUser
from .serializers import RobogalsUserSerializer


PAGINATION_MAX_LENGTH = 1000



class ListUsers(APIView):
    def metadata(self, request):
        """
        Don't include the view description in OPTIONS responses.
        """ 
        data = super(ListUsers, self).metadata(request)
        data.pop('description')
        return data
    
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
            if field_name in RobogalsUser.PROTECTED_FIELDS:
                return Response({"detail":"`{}` is a protected field.".format(field_name)}, status=status.HTTP_400_BAD_REQUEST)
            
            # Non-valid field names
            # ! Uses _meta non-documented API
            try:
                RobogalsUser._meta.get_field_by_name(field_name)
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
        query = RobogalsUser.objects.filter(is_active=True)
        query = query.filter(**filter_dict)
        query = query.order_by(*sort_fields)
        
        query_size = query.count()
        
        query = query[pagination_start_index:pagination_end_index]
        
        
        # Serialize
        serializer = RobogalsUserSerializer
        serializer.Meta.fields = fields
        
        serialized_query = serializer(query, many=True)
        
        
        # Output
        output_user_list = []
        
        for user_object in serialized_query.data:
            new_dict = {}
            new_dict.update({"id": user_object.pop("id")})
            new_dict.update({"data": user_object})
        
            output_user_list.append(new_dict)
        
        
        return Response({
                            "meta": {
                                "size": query_size
                            },
                            "user": output_user_list
                        })

class DeleteUsers(APIView):
    def metadata(self, request):
        """
        Don't include the view description in OPTIONS responses.
        """ 
        data = super(DeleteUsers, self).metadata(request)
        data.pop('description')
        return data
        
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
                
            if request.user.is_authenticated():
                if pk == request.user.pk:
                    ids_to_remove.append(idx)
                    failed_ids.update({pk: "OBJECT_SELF_NOT_DELETABLE"})
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
                query = RobogalsUser.objects.filter(is_active=True, pk__in=requested_ids)
                affected_ids = [obj.get("id") for obj in query.values("id")]
                affected_num_rows = query.update(is_active=False)
        except:
            for pk in requested_ids:
                failed_ids.update({pk: "OBJECT_NOT_MODIFIED"})

        # Gather up non-deleted IDs
        non_deleted_ids = list(set(requested_ids)-set(affected_ids))
        
        for pk in non_deleted_ids:
            failed_ids.update({pk: "OBJECT_NOT_MODIFIED"})
        
        
        
        return Response({
            "fail": {
                "id": failed_ids
            },
            "success": {
                "id": affected_ids
            }
        })
        

class EditUsers(APIView):    
    def metadata(self, request):
        """
        Don't include the view description in OPTIONS responses.
        """ 
        data = super(EditUsers, self).metadata(request)
        data.pop('description')
        return data
        
    def post(self, request, format=None):
        # request.DATA
        try:
            supplied_users = list(request.DATA.get("user"))
        except:
            return Response({"detail":"DATA_FORMAT_INVALID"}, status=status.HTTP_400_BAD_REQUEST)
                
        failed_user_updates = {}
        completed_user_updates = []
        
        # Filter out bad data
        for user_object in supplied_users:
            skip_user = False
            user_update_dict = {}
            
            
            try:
                user_id = str(user_object.get("id"))
                user_data = dict(user_object.get("data"))
            except:
                return Response({"detail":"DATA_FORMAT_INVALID"}, status=status.HTTP_400_BAD_REQUEST)
            
            if (user_id is None):
                return Response({"detail":"DATA_INSUFFICIENT"}, status=status.HTTP_400_BAD_REQUEST)
            
            for field,value in user_data.items():
                field = str(field)
                
                # Read only fields
                if field in RobogalsUser.READONLY_FIELDS:
                    failed_user_updates.update({user_id: "FIELD_READ_ONLY"})
                    skip_user = True
                    break
                
                # Non-valid field names
                # ! Uses _meta non-documented API
                try:
                    RobogalsUser._meta.get_field_by_name(field)
                except FieldDoesNotExist:
                    failed_user_updates.update({user_id: "FIELD_IDENTIFIER_INVALID"})
                    skip_user = True
                    break
                
                ################################################################
                # Permission restricted editing to be implemented here
                #
                # if not permission_allows_editing_of_this_id:
                #   failed_user_updates.update({pk: "PERMISSION_DENIED"})
                #   skip_user = True
                #   break
                ################################################################
            
                # Add to update data dict
                user_update_dict.update({field: value})
            
            if skip_user:
                continue
            
            
            # Fetch, serialise and save
            try:
                user_query = RobogalsUser.objects.get(is_active=True, pk=user_id)
            except:
                failed_user_updates.update({user_id: "OBJECT_NOT_FOUND"})
                continue
                
            serializer = RobogalsUserSerializer
            serialized_user = serializer(user_query, data=user_update_dict, partial=True)
        
            if serialized_user.is_valid():
                try:
                    with transaction.atomic():
                        serialized_user.save()
                        completed_user_updates.append(user_id)
                except:
                    failed_user_updates.update({user_id: "OBJECT_NOT_MODIFIED"})
            else:
                failed_user_updates.update({user_id: "DATA_VALIDATION_FAILED"})
                
        return Response({
            "fail": {
                "id": failed_user_updates
            },
            "success": {
                "id": completed_user_updates
            }
        })

        

class CreateUsers(APIView):    
    def metadata(self, request):
        """
        Don't include the view description in OPTIONS responses.
        """ 
        data = super(CreateUsers, self).metadata(request)
        data.pop('description')
        return data
        
    def post(self, request, format=None):
        # request.DATA
        try:
            supplied_users = list(request.DATA.get("user"))
        except:
            return Response({"detail":"DATA_FORMAT_INVALID"}, status=status.HTTP_400_BAD_REQUEST)
                
        failed_user_creations = {}
        completed_user_creations = {}
        
        # Filter out bad data
        for user_object in supplied_users:
            skip_user = False
            user_create_dict = {}
            
            try:
                user_nonce = user_object.get("nonce")
                user_data = dict(user_object.get("data"))
            except:
                return Response({"detail":"DATA_FORMAT_INVALID"}, status=status.HTTP_400_BAD_REQUEST)
            
            if (user_nonce is None):
                return Response({"detail":"DATA_INSUFFICIENT"}, status=status.HTTP_400_BAD_REQUEST)
            
            for field,value in user_data.items():
                field = str(field)
                
                # Read only fields
                if field in RobogalsUser.READONLY_FIELDS:
                    failed_user_creations.update({user_nonce: "FIELD_READ_ONLY"})
                    skip_user = True
                    break
                
                # Non-valid field names
                # ! Uses _meta non-documented API
                try:
                    RobogalsUser._meta.get_field_by_name(field)
                except FieldDoesNotExist:
                    failed_user_creations.update({user_nonce: "FIELD_IDENTIFIER_INVALID"})
                    skip_user = True
                    break
            
                if field == "primary_email":
                    if RobogalsUser.objects.filter(primary_email=value).count():
                        failed_user_creations.update({user_nonce: "OBJECT_ALREADY_EXISTS"})
                        skip_user = True
                        break
            
                # Add to update data dict
                user_create_dict.update({field: value})
            
            if skip_user:
                continue
            
            
            # Serialise and save
            serializer = RobogalsUserSerializer
            serialized_user = serializer(data=user_create_dict)
            
            if serialized_user.is_valid():
                try:
                    with transaction.atomic():
                        user = serialized_user.save()
                        completed_user_creations.update({user_nonce: user.pk})
                except:
                    failed_user_creations.update({user_nonce: "OBJECT_NOT_MODIFIED"})
            else:
                failed_user_creations.update({user_nonce: "DATA_VALIDATION_FAILED"})
                
        return Response({
            "fail": {
                "nonce": failed_user_creations
            },
            "success": {
                "nonce_id": completed_user_creations
            }
        })
        
        

class ResetUserPasswords(APIView):    
    def metadata(self, request):
        """
        Don't include the view description in OPTIONS responses.
        """ 
        data = super(ResetUserPasswords, self).metadata(request)
        data.pop('description')
        return data
        
    def post(self, request, format=None):
        # request.DATA
        try:
            primary_emails = list(request.DATA.get("primary_email"))
        except:
            return Response({"detail":"DATA_FORMAT_INVALID"}, status=status.HTTP_400_BAD_REQUEST)
                
        failed_resets = {}
        
        # Run query
        query = RobogalsUser.objects.filter(primary_email__in=primary_emails)
        
        ##### <<<< RESET CODE HERE >>>>
        
        
        
        # There is no OBJECT_NOT_FOUND response for privacy and security reasons
        return Response({
            "fail": {
                "primary_email": {}
            },
            "success": {
                "primary_email": primary_emails
            }
        })
        
        
        
class WhoAmI(APIView):
    permission_classes = (IsAuthenticated,)
    
    def metadata(self, request):
        """
        Don't include the view description in OPTIONS responses.
        """ 
        data = super(WhoAmI, self).metadata(request)
        data.pop('description')
        return data

    def post(self, request, format=None):
        from myrg_groups.serializers import GroupSerializer, RoleClassSerializer
        
        # request
        user_id = request.user.pk
        role_id = request.DATA.get("role")
        
        group_id = None
        role_class_id = None
        
        group_data = {}
        role_class_data = {}
        
        # Build query
        try:
            user_query = request.user
            
            if not (role_id is None):
                role_query = user_query.role_set.filter(Q(date_start__lte=timezone.now()) & (Q(date_end__isnull=True) | Q(date_end__gte=timezone.now()))).get(pk = str(role_id))
                
        except:
            return Response({"detail":"ROLE_INVALID"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Serialize
        user_serializer = RobogalsUserSerializer
        user_serializer.Meta.fields = ("display_name","username","primary_email",)
        user_serialized_query = user_serializer(user_query)
        
        
        
        # Role -> Group, Role Class
        if not (role_id is None):
            group = role_query.group
            group_id = group.id
            
            role_class = role_query.role_class
            role_class_id = role_class.id

            group_serializer = GroupSerializer
            group_serializer.Meta.fields = ("name",)
            group_serialized_query = group_serializer(group)
            group_data = group_serialized_query.data
            
            role_class_serializer = RoleClassSerializer
            role_class_serializer.Meta.fields = ("name",)
            role_class_serialized_query = role_class_serializer(role_class)
            role_class_data = role_class_serialized_query.data
        
        
        
        return Response({
            "user": {
                "data": user_serialized_query.data,
                "id": user_id,
            },
            "role_class": {
                "data": role_class_data,
                "id": role_class_id,
            },
            "group": {
                "data": group_data,
                "id": group_id,
            },
        })       
        
class KillSessions(APIView):
    permission_classes = (IsAuthenticated,)
    
    def metadata(self, request):
        """
        Don't include the view description in OPTIONS responses.
        """ 
        data = super(KillSessions, self).metadata(request)
        data.pop('description')
        return data

    def post(self, request, format=None):
        return Response({
            "fail": {
            },
            "success": {
                "sessions_deleted":  request.user.delete_all_unexpired_sessions()
            }
        })

