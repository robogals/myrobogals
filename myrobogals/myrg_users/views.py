from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions

from django.core import serializers
import json

from .models import RobogalsUser

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
                    # "order": ""
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
            
            
        
        
        # Build query
        query = RobogalsUser.objects.all()
        
        # Filter
        filter_dict = {}
        sort_dict = {}
        columns = []
        
        for definition in requested_columns:
            field = definition.get("field")
            field_query = definition.get("query")
            field_order = definition.get("order")
            
            if (field is None):
                return Response({"detail":"Insufficient information."})
            
            field = str(field)
            
            columns.append(field)
            
            if (field_query is not None):
                filter_dict.update({field+"__icontains": str(field_query)})
            
            #if (field_order is not None):
            #    sort_dict.update({field: str(field_order)})

        
        
        query = query.filter(**filter_dict)
        query = query[pagination_start_index:pagination_end_index]
        query = query.values(*columns)
        
        
        
        
        # Pull out the columns ("request")
        # Limit queries by "pagination"
        
        
        
        
        
        return Response(query)