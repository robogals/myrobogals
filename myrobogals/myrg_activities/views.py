from __future__ import unicode_literals
from future.builtins import *
import six

from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.db.models.fields import FieldDoesNotExist
from django.db.models import Q
from django.db import transaction
from django.utils import timezone

from .models import Activity
from .serializers import ActivitySerializer

class ListActivities(APIView):
    def metadata(self, request):
        """
        Don't include the view description in OPTIONS responses.
        """ 
        data = super(ListActivities, self).metadata(request)
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
        
        
        # Activity model
        serializer = ActivitySerializer
        activity_model = Activity
        
        serializer.Meta.model = activity_model
        
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
            if field_name in activity_model.PROTECTED_FIELDS:
                return Response({"detail":"`{}` is a protected field.".format(field_name)}, status=status.HTTP_400_BAD_REQUEST)
            
            # Non-valid field names
            # ! Uses _meta non-documented API
            try:
                activity_model._meta.get_field_by_name(field_name)
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
        query = activity_model.objects.filter(status__gt=1)
        query = query.filter(**filter_dict)
        query = query.order_by(*sort_fields)
        
        query_size = query.count()
        
        query = query[pagination_start_index:pagination_end_index]
        
        
        # Serialize
        serializer.Meta.fields = fields
        serialized_query = serializer(query, many=True)
        
        
        # Output
        output_list = []
        
        for activity_object in serialized_query.data:
            new_dict = {}
            new_dict.update({"id": activity_object.pop("id")})
            new_dict.update({"data": activity_object})
        
            output_list.append(new_dict)
        
        
        return Response({
                            "meta": {
                                "size": query_size
                            },
                            "activity": output_list
                        })

