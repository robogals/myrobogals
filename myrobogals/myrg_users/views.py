from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions

from django.core import serializers
import json

from .models import RobogalsUser
from .serializers import RobogalsUserSerializer

class ListUsers(APIView):
    """
    View to list all users in the system.

    * Requires token authentication.
    * Only admin users are able to access this view.
    """
    authentication_classes = (authentication.SessionAuthentication,authentication.BasicAuthentication,)
    permission_classes = (permissions.IsAdminUser,)
    
    
    def post(self, request, format=None):
        """
        Return a list of users limited to queries.
        """
        # Sample input request JSON
        # {
            # "result": [ --- required
                # {
                    # "field": "",
                    # "query": "",
                    # "order": "",
                    # "visibility": "",
                # },
                # ...
            # ],
            # "pagination": { --- required
                # "limit": 0,
                # "page": 0
            # }
        # }
        
        
        # Parse the request.DATA
        requested_columns = request.DATA.get("result")
        requested_pagination = request.DATA.get("pagination")
        
        if (not requested_columns) or (not requested_pagination):
            return Response({"detail":"Insufficient information."})
        
        
        # Pagination
        pagination_page_index = requested_pagination.get("page")
        pagination_page_length = requested_pagination.get("limit")
        
        if (pagination_page_index is None) or (pagination_page_length is None):
            return Response({"detail":"Insufficient information."})
        
        pagination_start_index = pagination_page_index * pagination_page_length
        pagination_end_index = pagination_start_index + pagination_page_length
            
        if pagination_start_index < 0 or pagination_end_index < 0:
            return Response({"detail":"Negative indexing not supported."})
        
        
        
        # Build query
        query = RobogalsUser.objects.filter(is_active=True)
        
        # Filter
        filter_dict = {}
        sort_columns = []
        columns = []
        
        for definition in requested_columns:
            field = definition.get("field")
            field_query = definition.get("query")
            field_order = definition.get("order")
            field_visibility = definition.get("visibility")
            
            if (field is None):
                return Response({"detail":"Insufficient information."})
            
            field = str(field)
            
            if (field_query is not None):
                filter_dict.update({field+"__icontains": str(field_query)})
            
            if (field_order is not None):
                field_order = str(field_order)
                
                if field_order == "a":
                    sort_columns.append(field)
                if field_order == "d":
                    sort_columns.append("-"+field)
            
            if not (field_visibility == False):
                columns.append(field)
        
        query = query.filter(**filter_dict)
        query = query.order_by(*sort_columns)
        query = query[pagination_start_index:pagination_end_index]
        
        serializer = RobogalsUserSerializer
        serializer.Meta.fields = columns
        
        serialized_query = serializer(query, many=True)
        
        return Response(serialized_query.data)

class DeleteUsers(APIView):
    authentication_classes = (authentication.SessionAuthentication,authentication.BasicAuthentication,)
    permission_classes = (permissions.IsAdminUser,)
    
    def post(self, request, format=None):
        # {
            # "id": [pk, ...]
        # }
        
        requested_ids = request.DATA.get("id")
        
        if (not requested_ids):
            return Response({"detail":"Insufficient information."})
        
        if not all(isinstance(pk, int) for pk in requested_ids):
            return Response({"detail":"ID list is not valid."})
        
        query = RobogalsUser.objects.filter(id__in=requested_ids)
        number_of_rows = query.update(is_active=False)
        
        return Response({"detail":"User deletion successful.", "affected_rows": number_of_rows, "id": requested_ids})
        