from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.db.models.fields import FieldDoesNotExist

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
        requested_fields = request.DATA.get("query")
        requested_pagination = request.DATA.get("pagination")
        
        if (not requested_fields) or (not requested_pagination):
            return Response({"detail":"Insufficient information."}, status=status.HTTP_400_BAD_REQUEST)
        
        
        # Pagination
        pagination_page_index = requested_pagination.get("page")
        pagination_page_length = requested_pagination.get("length")
        
        if (pagination_page_index is None) or (pagination_page_length is None):
            return Response({"detail":"Insufficient information."}, status=status.HTTP_400_BAD_REQUEST)
        
        pagination_page_index = int(pagination_page_index)
        pagination_page_length = int(pagination_page_length)
        
        pagination_start_index = pagination_page_index * pagination_page_length
        pagination_end_index = pagination_start_index + (pagination_page_length if pagination_page_length < PAGINATION_MAX_LENGTH else PAGINATION_MAX_LENGTH)
            
        if pagination_start_index < 0 or pagination_end_index < 0:
            return Response({"detail":"Negative indexing not supported."}, status=status.HTTP_400_BAD_REQUEST)
        
        
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
                return Response({"detail":"`name` expected."}, status=status.HTTP_400_BAD_REQUEST)
            
            field_name = str(field_name)
            
            # Skip anything to do with protected fields like passwords
            if field_name in RobogalsUser.PROTECTED_FIELDS:
                continue
            
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
                            "user": output_user_list,
                            "pagination": {
                                "size": query_size
                            }
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
        requested_ids = request.DATA.get("id")
        
        if (not requested_ids):
            return Response({"detail":"Insufficient information."}, status=status.HTTP_400_BAD_REQUEST)
        
        if not all(isinstance(pk, int) for pk in requested_ids):
            return Response({"detail":"`id` is not valid."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Run query
        query = RobogalsUser.objects.filter(is_active=True, id__in=requested_ids)
        affected_ids = [obj.get("id") for obj in query.values("id")]
        affected_num_rows = query.update(is_active=False)
        
        return Response({
            # "affected_rows": affected_num_rows,
            "id": affected_ids
        })
        

class EditUsers(APIView):
    """
    ## Description ##
    An API endpoint to edit users.
    
    Requests must only be made via. POST. Authentication is required.
    
    Requests are atomic; they will either successfully process all of the requested changes or none at all.
    
    To change the "deleted" status of a user, use `/users/delete`.
    
    ## Example ##
    Input:
    
        {
            "user":   [
                {
                    "id": 42,
                    "data": {
                        "primary_email": "arthur.dent@robogals.org"
                    }
                },
                {
                    "id": 83,
                    "data": {
                        "username": "JohnDoe",
                        "preferred_name": "John Doe"
                    }
                },
                {
                    "id": 111,
                    "data": {
                        "password": "ThisIsSomeNewPassword"
                    }
                }
            ]
        }
    
    Output:
    
    
    ## Parameters ##
    Required parameters are _**emphasised**_.
    <table width="100%" border="1" cellpadding="5" style="font-family: monospace;">
        <tr>
            <td>_**user[]**_</td>
            <td>List of users to edit information on.</td>
        </tr>
    </table>
    """
    
    def metadata(self, request):
        """
        Don't include the view description in OPTIONS responses.
        """ 
        data = super(EditUsers, self).metadata(request)
        data.pop('description')
        return data
        
    def post(self, request, format=None):
        # request.DATA
        supplied_users = request.DATA.get("user")
        
        # Filter
        user_update_dict = {}
        
        for user_object in supplied_users:
            user_id = user_object.get("id")
            user_data = user_object.get("data")
            
            if (user_id is None):
                return Response({"detail":"`id` expected."}, status=status.HTTP_400_BAD_REQUEST)
            
            for field, value in user_data:
                field = str(field)
                
                # Read only fields
                if field in RobogalsUser.READONLY_FIELDS:
                    return Response({"detail":"`{}` is a read-only field.".format(field)}, status=status.HTTP_400_BAD_REQUEST)
                
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
        
        query = query.filter(**filter_dict)
        query = query.order_by(*sort_fields)
        query = query[pagination_start_index:pagination_end_index]
        
        # Serialize
        serializer = RobogalsUserSerializer
        serializer.Meta.fields = fields
        
        serialized_query = serializer(query, many=True)
        
        return Response(serialized_query.data)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        # if (not requested_ids):
            # return Response({"detail":"Insufficient information."}, status=status.HTTP_400_BAD_REQUEST)
        
        # if not all(isinstance(pk, int) for pk in requested_ids):
            # return Response({"detail":"`id` is not valid."}, status=status.HTTP_400_BAD_REQUEST)
        
        # # Run query
        # query = RobogalsUser.objects.filter(is_active=True, id__in=requested_ids)
        # affected_ids = [obj.get("id") for obj in query.values("id")]
        # affected_num_rows = query.update(is_active=False)
        
        # return Response({
            # "affected_rows": affected_num_rows,
            # "id": affected_ids
        # })
        