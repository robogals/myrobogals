"""
    myRobogals
    myrg_core/classes.py

    2014
    Robogals Software Team
"""
from rest_framework import status, exceptions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils.datastructures import SortedDict

from .functions import log_api_call

from django.db.models import Q
from django.db import transaction
from django.utils import timezone

class RoleInvalidException(exceptions.APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "ROLE_INVALID"
    
class CallNotProcessedException(exceptions.APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "CALL_NOT_PROCESSED"

class RobogalsAPIView(APIView):
    role_obj = None
    role_id = None
    user_obj = None
    user_id = None
    
    def initial(self, request, *args, **kwargs):
        """
        Runs anything that needs to occur prior to calling the method handler.
        """
        self.format_kwarg = self.get_format_suffix(**kwargs)
        
        # Set user/role information
        user_obj = request.user
        role_id = request.DATA.get("role_id")
                
        if user_obj.is_authenticated():
            self.user_obj = user_obj
            self.user_id = user_obj.pk
        
        if role_id is None:
            role_id = request.session.get("role_id")
        
        role_query = None
        
        try:
            if not (role_id is None):
                role_query = user_obj.role_set.filter(Q(date_start__lte=timezone.now()) & (Q(date_end__isnull=True) | Q(date_end__gte=timezone.now()))).get(pk = str(role_id))
                self.role_id = role_id
                self.role_obj = role_query
        except:
            raise RoleInvalidException()
            
        # Log the call
        if not log_api_call(request, role_query):
            raise CallNotProcessedException()
            
            
        # Ensure that the incoming request is permitted
        self.perform_authentication(request)
        self.check_permissions(request)
        self.check_throttles(request)

        # Perform content negotiation and store the accepted info on the request
        neg = self.perform_content_negotiation(request)
        request.accepted_renderer, request.accepted_media_type = neg
        
        
         
    def metadata(self, request):
        """
        Return a dictionary of metadata about the view.
        Used to return responses for OPTIONS requests.
        """
        # By default we can't provide any form-like information, however the
        # generic views override this implementation and add additional
        # information for POST and PUT methods, based on the serializer.
        ret = SortedDict()
        ret['name'] = self.get_view_name()
        #ret['description'] = self.get_view_description()
        ret['renders'] = [renderer.media_type for renderer in self.renderer_classes]
        ret['parses'] = [parser.media_type for parser in self.parser_classes]
        return ret