from myrg_core.classes import RobogalsAPIView
from rest_framework.response import Response
from rest_framework import status

from django.db.models.fields import FieldDoesNotExist
from django.db.models import Q
from django.db import transaction
from django.utils import timezone

from .models import Group, Chapter, School, Company, RoleClass, Role
from .serializers import GroupSerializer, RoleClassSerializer, RoleSerializer


PAGINATION_MAX_LENGTH = 1000

        
# Group
################################################################################
class ListGroups(RobogalsAPIView):
    def post(self, request, format=None):
        # request.DATA
        try:
            requested_fields = list(request.DATA.get("query"))
            requested_group = dict(request.DATA.get("group"))
            requested_pagination = dict(request.DATA.get("pagination"))
        except:
            return Response({"detail":"DATA_FORMAT_INVALID"}, status=status.HTTP_400_BAD_REQUEST)
            
        if (not requested_fields) or (not requested_pagination) or (not requested_group):
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
        
        
        # Group model
        serializer = GroupSerializer
        
        if requested_group.get("type") == 'chapters':
            group_model = Chapter
        elif requested_group.get("type") == 'schools':
            group_model = School
        elif requested_group.get("type") == 'companies':
            group_model = Company
        elif requested_group.get("type") == 'general':
            group_model = Group
        else:
            return Response({"detail":"DATA_INVALID"}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer.Meta.model = group_model
        
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
            if field_name in group_model.PROTECTED_FIELDS:
                return Response({"detail":"`{}` is a protected field.".format(field_name)}, status=status.HTTP_400_BAD_REQUEST)
            
            # Non-valid field names
            # ! Uses _meta non-documented API
            try:
                group_model._meta.get_field_by_name(field_name)
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
        query = group_model.objects.filter(status__gt=0)
        query = query.filter(**filter_dict)
        query = query.order_by(*sort_fields)
        
        query_size = query.count()
        
        query = query[pagination_start_index:pagination_end_index]
        
        
        # Serialize
        serializer.Meta.fields = fields
        serialized_query = serializer(query, many=True)
        
        
        # Output
        output_list = []
        
        for group_object in serialized_query.data:
            new_dict = {}
            new_dict.update({"id": group_object.pop("id")})
            new_dict.update({"data": group_object})
        
            output_list.append(new_dict)
        
        
        return Response({
                            "meta": {
                                "size": query_size
                            },
                            "group": output_list
                        })

class DeleteGroups(RobogalsAPIView):
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
                query = Group.objects.filter(status__gt=0, id__in=requested_ids)
                affected_ids = [obj.get("id") for obj in query.values("id")]
                affected_num_rows = query.update(status=0)
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
        
class EditGroups(RobogalsAPIView):
    def post(self, request, format=None):
        # request.DATA
        try:
            supplied_groups = list(request.DATA.get("group"))
        except:
            return Response({"detail":"DATA_FORMAT_INVALID"}, status=status.HTTP_400_BAD_REQUEST)
                
        failed_group_updates = {}
        completed_group_updates = []
        
        # Filter out bad data
        for group_object in supplied_groups:
            skip_group = False
            group_update_dict = {}
            
            
            try:
                group_id = int(group_object.get("id"))
                group_data = dict(group_object.get("data"))
            except:
                return Response({"detail":"DATA_FORMAT_INVALID"}, status=status.HTTP_400_BAD_REQUEST)
            
            if (group_id is None):
                return Response({"detail":"DATA_INSUFFICIENT"}, status=status.HTTP_400_BAD_REQUEST)
            
            for field,value in group_data.items():
                field = str(field)
                
                # Read only fields
                if field in Group.READONLY_FIELDS or field == "creator":
                    failed_group_updates.update({group_id: "FIELD_READ_ONLY"})
                    skip_group = True
                    break
                
                # Non-valid field names
                # ! Uses _meta non-documented API
                try:
                    Group._meta.get_field_by_name(field)
                except FieldDoesNotExist:
                    failed_group_updates.update({group_id: "FIELD_IDENTIFIER_INVALID"})
                    skip_group = True
                    break
                    
                ################################################################
                # Permission restricted editing to be implemented here
                #
                # if not permission_allows_editing_of_this_id:
                #   failed_group_updates.update({pk: "PERMISSION_DENIED"})
                #   skip_group = True
                #   break
                ################################################################
            
                # Add to update data dict
                group_update_dict.update({field: value})
            
            if skip_group:
                continue
            
            
            # Fetch, serialise and save
            try:
                group_query = Group.objects.get(status__gt=0, pk=group_id)
            except:
                failed_group_updates.update({group_id: "OBJECT_NOT_FOUND"})
                continue
                
            serializer = GroupSerializer
            serialized_group = serializer(group_query, data=group_update_dict, partial=True)
        
            if serialized_group.is_valid():
                try:
                    with transaction.atomic():
                        serialized_group.save()
                        completed_group_updates.append(group_id)
                except:
                    failed_group_updates.update({group_id: "OBJECT_NOT_MODIFIED"})
            else:
                failed_group_updates.update({group_id: "DATA_VALIDATION_FAILED"})
                
        return Response({
            "fail": {
                "id": failed_group_updates
            },
            "success": {
                "id": completed_group_updates
            }
        })

class CreateGroups(RobogalsAPIView):
    def post(self, request, format=None):
        # request.DATA
        try:
            supplied_groups = list(request.DATA.get("group"))
        except:
            return Response({"detail":"DATA_FORMAT_INVALID"}, status=status.HTTP_400_BAD_REQUEST)
                
        failed_group_creations = {}
        completed_group_creations = {}
        
        # Filter out bad data
        for group_object in supplied_groups:
            skip_group = False
            group_create_dict = {}
            
            try:
                group_nonce = group_object.get("nonce")
                group_data = dict(group_object.get("data"))
            except:
                return Response({"detail":"DATA_FORMAT_INVALID"}, status=status.HTTP_400_BAD_REQUEST)
            
            if (group_nonce is None):
                return Response({"detail":"DATA_INSUFFICIENT"}, status=status.HTTP_400_BAD_REQUEST)
            
            for field,value in group_data.items():
                field = str(field)
                
                # Read only fields
                if field in Group.READONLY_FIELDS or field == "creator":
                    failed_group_creations.update({group_nonce: "FIELD_READ_ONLY"})
                    skip_group = True
                    break
                
                # Non-valid field names
                # ! Uses _meta non-documented API
                try:
                    Group._meta.get_field_by_name(field)
                except FieldDoesNotExist:
                    failed_group_creations.update({group_nonce: "FIELD_IDENTIFIER_INVALID"})
                    skip_group = True
                    break
            
            
                # Add to update data dict
                group_create_dict.update({field: value})
            
            if skip_group:
                continue
            
            # Creator is the requester
            group_create_dict.update({"creator": request.user.pk})
        
            # Group model
            serializer = GroupSerializer
            
            if requested_group.get("type") == 'chapters':
                group_model = Chapter
            elif requested_group.get("type") == 'schools':
                group_model = School
            elif requested_group.get("type") == 'companies':
                group_model = Company
            elif requested_group.get("type") == 'general':
                group_model = Group
            else:
                return Response({"detail":"DATA_INVALID"}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer.Meta.model = group_model
        
        
            # Serialise and save
            serialized_group = serializer(data=group_create_dict)
            
            if serialized_group.is_valid():
                try:
                    with transaction.atomic():
                        group = serialized_group.save()
                        completed_group_creations.update({group_nonce: group.id})
                except:
                    failed_group_creations.update({group_nonce: "OBJECT_NOT_MODIFIED"})
            else:
                failed_group_creations.update({group_nonce: "DATA_VALIDATION_FAILED"})
                
        return Response({
            "fail": {
                "nonce": failed_group_creations
            },
            "success": {
                "nonce_id": completed_group_creations
            }
        })

        
        
# Role Class
################################################################################
class ListRoleClasses(RobogalsAPIView):
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
            if field_name in RoleClass.PROTECTED_FIELDS:
                return Response({"detail":"`{}` is a protected field.".format(field_name)}, status=status.HTTP_400_BAD_REQUEST)
            
            # Non-valid field names
            # ! Uses _meta non-documented API
            try:
                RoleClass._meta.get_field_by_name(field_name)
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
        query = RoleClass.objects.filter(is_active=True)
        query = query.filter(**filter_dict)
        query = query.order_by(*sort_fields)
        
        query_size = query.count()
        
        query = query[pagination_start_index:pagination_end_index]
        
        
        # Serialize
        serializer = RoleClassSerializer
        serializer.Meta.fields = fields
        
        serialized_query = serializer(query, many=True)
        
        
        # Output
        output_list = []
        
        for roleclass_object in serialized_query.data:
            new_dict = {}
            new_dict.update({"id": roleclass_object.pop("id")})
            new_dict.update({"data": roleclass_object})
        
            output_list.append(new_dict)
        
        
        return Response({
                            "meta": {
                                "size": query_size
                            },
                            "role_class": output_list
                        })

class DeleteRoleClasses(RobogalsAPIView):
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
                query = RoleClass.objects.filter(is_active=True, id__in=requested_ids)
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
        
class EditRoleClasses(RobogalsAPIView):
    def post(self, request, format=None):
        # request.DATA
        try:
            supplied_roleclasses = list(request.DATA.get("role_class"))
        except:
            return Response({"detail":"DATA_FORMAT_INVALID"}, status=status.HTTP_400_BAD_REQUEST)
                
        failed_roleclass_updates = {}
        completed_roleclass_updates = []
        
        # Filter out bad data
        for roleclass_object in supplied_roleclasses:
            skip_roleclass = False
            roleclass_update_dict = {}
            
            
            try:
                roleclass_id = int(roleclass_object.get("id"))
                roleclass_data = dict(roleclass_object.get("data"))
            except:
                return Response({"detail":"DATA_FORMAT_INVALID"}, status=status.HTTP_400_BAD_REQUEST)
            
            if (roleclass_id is None):
                return Response({"detail":"DATA_INSUFFICIENT"}, status=status.HTTP_400_BAD_REQUEST)
            
            for field,value in roleclass_data.items():
                field = str(field)
                
                # Read only fields
                if field in RoleClass.READONLY_FIELDS:
                    failed_roleclass_updates.update({roleclass_id: "FIELD_READ_ONLY"})
                    skip_roleclass = True
                    break
                
                # Non-valid field names
                # ! Uses _meta non-documented API
                try:
                    RoleClass._meta.get_field_by_name(field)
                except FieldDoesNotExist:
                    failed_roleclass_updates.update({roleclass_id: "FIELD_IDENTIFIER_INVALID"})
                    skip_roleclass = True
                    break
                    
                ################################################################
                # Permission restricted editing to be implemented here
                #
                # if not permission_allows_editing_of_this_id:
                #   failed_roleclass_updates.update({pk: "PERMISSION_DENIED"})
                #   skip_roleclass = True
                #   break
                ################################################################
            
                # Add to update data dict
                roleclass_update_dict.update({field: value})
            
            if skip_roleclass:
                continue
            
            
            # Fetch, serialise and save
            try:
                roleclass_query = RoleClass.objects.get(status__gt=0, pk=roleclass_id)
            except:
                failed_roleclass_updates.update({roleclass_id: "OBJECT_NOT_FOUND"})
                continue
                
            serializer = RoleClassSerializer
            serialized_group = serializer(roleclass_query, data=roleclass_update_dict, partial=True)
        
            if serialized_roleclass.is_valid():
                try:
                    with transaction.atomic():
                        serialized_roleclass.save()
                        completed_roleclass_updates.append(roleclass_id)
                except:
                    failed_roleclass_updates.update({roleclass_id: "OBJECT_NOT_MODIFIED"})
            else:
                failed_roleclass_updates.update({roleclass_id: "DATA_VALIDATION_FAILED"})
                
        return Response({
            "fail": {
                "id": failed_roleclass_updates
            },
            "success": {
                "id": completed_roleclass_updates
            }
        })

class CreateRoleClasses(RobogalsAPIView):
    def post(self, request, format=None):
        # request.DATA
        try:
            supplied_roleclasses = list(request.DATA.get("role_class"))
        except:
            return Response({"detail":"DATA_FORMAT_INVALID"}, status=status.HTTP_400_BAD_REQUEST)
                
        failed_roleclass_creations = {}
        completed_roleclass_creations = {}
        
        # Filter out bad data
        for roleclass_object in supplied_roleclasses:
            skip_roleclass = False
            roleclass_create_dict = {}
            
            try:
                roleclass_nonce = roleclass_object.get("nonce")
                roleclass_data = dict(roleclass_object.get("data"))
            except:
                return Response({"detail":"DATA_FORMAT_INVALID"}, status=status.HTTP_400_BAD_REQUEST)
            
            if (roleclass_nonce is None):
                return Response({"detail":"DATA_INSUFFICIENT"}, status=status.HTTP_400_BAD_REQUEST)
            
            for field,value in roleclass_data.items():
                field = str(field)
                
                # Read only fields
                if field in RoleClass.READONLY_FIELDS:
                    failed_roleclass_creations.update({roleclass_nonce: "FIELD_READ_ONLY"})
                    skip_roleclass = True
                    break
                
                # Non-valid field names
                # ! Uses _meta non-documented API
                try:
                    RoleClass._meta.get_field_by_name(field)
                except FieldDoesNotExist:
                    failed_roleclass_creations.update({roleclass_nonce: "FIELD_IDENTIFIER_INVALID"})
                    skip_roleclass = True
                    break
            
            
                # Add to update data dict
                roleclass_create_dict.update({field: value})
            
            if skip_roleclass:
                continue
            
            # Serialise and save
            serializer = RoleClassSerializer
            serialized_roleclass = serializer(data=roleclass_create_dict)
            
            if serialized_roleclass.is_valid():
                try:
                    with transaction.atomic():
                        roleclass = serialized_roleclass.save()
                        completed_roleclass_creations.update({roleclass_nonce: roleclass.id})
                except:
                    failed_roleclass_creations.update({roleclass_nonce: "OBJECT_NOT_MODIFIED"})
            else:
                failed_roleclass_creations.update({roleclass_nonce: "DATA_VALIDATION_FAILED"})
                
        return Response({
            "fail": {
                "nonce": failed_roleclass_creations
            },
            "success": {
                "nonce_id": completed_roleclass_creations
            }
        })
        
        
# Role
################################################################################
class ListRoles(RobogalsAPIView):
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
            if field_name in Role.PROTECTED_FIELDS:
                return Response({"detail":"`{}` is a protected field.".format(field_name)}, status=status.HTTP_400_BAD_REQUEST)
            
            # Non-valid field names
            # ! Uses _meta non-documented API
            try:
                Role._meta.get_field_by_name(field_name)
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
        query = Role.objects.filter(Q(date_start__lte=timezone.now()) & (Q(date_end__isnull=True) | Q(date_end__gte=timezone.now())))
        query = query.filter(**filter_dict)
        query = query.order_by(*sort_fields)
        
        query_size = query.count()
        
        query = query[pagination_start_index:pagination_end_index]
        
        
        # Serialize
        serializer = RoleSerializer
        serializer.Meta.fields = fields
        
        serialized_query = serializer(query, many=True)
        
        
        # Output
        output_list = []
        
        for role_object in serialized_query.data:
            new_dict = {}
            new_dict.update({"id": role_object.pop("id")})
            new_dict.update({"data": role_object})
        
            output_list.append(new_dict)
        
        
        return Response({
                            "meta": {
                                "size": query_size
                            },
                            "role": output_list
                        })

class EditRoles(RobogalsAPIView):
    def post(self, request, format=None):
        # request.DATA
        try:
            supplied_roles = list(request.DATA.get("role"))
        except:
            return Response({"detail":"DATA_FORMAT_INVALID"}, status=status.HTTP_400_BAD_REQUEST)
                
        failed_role_updates = {}
        completed_role_updates = []
        
        # Filter out bad data
        for role_object in supplied_roles:
            skip_role = False
            role_update_dict = {}
            
            
            try:
                role_id = int(role_object.get("id"))
                role_data = dict(role_object.get("data"))
            except:
                return Response({"detail":"DATA_FORMAT_INVALID"}, status=status.HTTP_400_BAD_REQUEST)
            
            if (role_id is None):
                return Response({"detail":"DATA_INSUFFICIENT"}, status=status.HTTP_400_BAD_REQUEST)
            
            for field,value in role_data.items():
                field = str(field)
                
                # Read only fields
                if field in Role.READONLY_FIELDS:
                    failed_role_updates.update({role_id: "FIELD_READ_ONLY"})
                    skip_role = True
                    break
                
                # Non-valid field names
                # ! Uses _meta non-documented API
                try:
                    Role._meta.get_field_by_name(field)
                except FieldDoesNotExist:
                    failed_role_updates.update({role_id: "FIELD_IDENTIFIER_INVALID"})
                    skip_role = True
                    break
                    
                ################################################################
                # Permission restricted editing to be implemented here
                #
                # if not permission_allows_editing_of_this_id:
                #   failed_role_updates.update({pk: "PERMISSION_DENIED"})
                #   skip_role = True
                #   break
                ################################################################
            
                # Add to update data dict
                role_update_dict.update({field: value})
            
            if skip_role:
                continue
            
            
            # Fetch, serialise and save
            try:
                role_query = Role.objects.get(pk=role_id)
            except:
                failed_role_updates.update({role_id: "OBJECT_NOT_FOUND"})
                continue
                
            serializer = RoleSerializer
            serialized_role = serializer(role_query, data=role_update_dict, partial=True)
        
            if serialized_role.is_valid():
                try:
                    with transaction.atomic():
                        serialized_role.save()
                        completed_role_updates.append(role_id)
                except:
                    failed_role_updates.update({role_id: "OBJECT_NOT_MODIFIED"})
            else:
                failed_role_updates.update({role_id: "DATA_VALIDATION_FAILED"})
                
        return Response({
            "fail": {
                "id": failed_role_updates
            },
            "success": {
                "id": completed_role_updates
            }
        })

class CreateRoles(RobogalsAPIView):
    def post(self, request, format=None):
        # request.DATA
        try:
            supplied_roles = list(request.DATA.get("role"))
        except:
            return Response({"detail":"DATA_FORMAT_INVALID"}, status=status.HTTP_400_BAD_REQUEST)
                
        failed_role_creations = {}
        completed_role_creations = {}
        
        # Filter out bad data
        for role_object in supplied_roles:
            skip_role = False
            role_create_dict = {}
            
            try:
                role_nonce = role_object.get("nonce")
                role_data = dict(role_object.get("data"))
            except:
                return Response({"detail":"DATA_FORMAT_INVALID"}, status=status.HTTP_400_BAD_REQUEST)
            
            if (role_nonce is None):
                return Response({"detail":"DATA_INSUFFICIENT"}, status=status.HTTP_400_BAD_REQUEST)
            
            for field,value in role_data.items():
                field = str(field)
                
                # Read only fields
                if field in Role.READONLY_FIELDS:
                    failed_role_creations.update({role_nonce: "FIELD_READ_ONLY"})
                    skip_role = True
                    break
                
                # Non-valid field names
                # ! Uses _meta non-documented API
                try:
                    Role._meta.get_field_by_name(field)
                except FieldDoesNotExist:
                    failed_role_creations.update({role_nonce: "FIELD_IDENTIFIER_INVALID"})
                    skip_role = True
                    break
            
            
                # Add to update data dict
                role_create_dict.update({field: value})
            
            if skip_role:
                continue
            
            
            # Serialise and save
            serializer = RoleSerializer
            serialized_role = serializer(data=role_create_dict)
            
            if serialized_role.is_valid():
                try:
                    with transaction.atomic():
                        role = serialized_role.save()
                        completed_role_creations.update({role_nonce: role.id})
                except:
                    failed_role_creations.update({role_nonce: "OBJECT_NOT_MODIFIED"})
            else:
                failed_role_creations.update({role_nonce: "DATA_VALIDATION_FAILED"})
                
        return Response({
            "fail": {
                "nonce": failed_role_creations
            },
            "success": {
                "nonce_id": completed_role_creations
            }
        })

        
        
        
        