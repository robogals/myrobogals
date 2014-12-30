from django.db import models
from django.test import TestCase
from django.test.client import RequestFactory
from rest_framework.permissions import BasePermission
from rest_framework.views import APIView
from myrg_core.classes import RobogalsAPIView
from .models import PermissionList
from .serializers import PermissionListSerializer
from myrg_groups.models import Role
from myrg_groups.serializers import RoleSerializer

# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

        
class PermissionManager(RobogalsAPIView):
    def get_classes_list(data):
        """
        Get all roleclasses based on permission provided
        """
        
        query = PermissionList.objects.filter(permission=data)

        return query[0].role_classes
    
    def get_userclass_by_user(user_id):
        """
        Get roleclasses based on user_id
        """
        query = Role.objects.filter(user=user_id)
            
        return query[0].role_class.id
        
    def owner(obj_id, user_id, model_obj):
        """
        Check the owner of the object, this function is mainly used for edit and delete method 
        """
        
        owner_obj = model_obj.objects.filter(id=obj_id)
        
        return user_id == owner_obj[0].user_id
        
    def permission_checked(obj_id, permission_type, user, model_obj):
        
        #granted default access for superuser
        if user.is_superuser:
           #logger.error("superuser permission is granted")
           return True
        
        #checked permission for owner of the object when the model is defined. It is used for edit and delete parmission
        if (model_obj is not None and "VIEW" not in permission_type):
            object_owner = PermissionManager.owner(obj_id, user.id, model_obj)
            if object_owner:
                #logger.error("owner's permission is granted")
                return True
        
        
        #granted permissions for listed user_id based on permission type
        PERMISSION_ID_ALLOWED = [int(i) for i in PermissionManager.get_classes_list(permission_type).split(',')]
        USER_ROLECLASS_ID = PermissionManager.get_userclass_by_user(user.id)    
        
        if USER_ROLECLASS_ID in PERMISSION_ID_ALLOWED:
            #logger.error("permission to view granted")
            return True    
        
        return False

class AnyPermissions(BasePermission):

    def get_permissions(self, view):
        """
        Get all of the permissions that are associated with the view.
        """

        permissions = getattr(view, "any_permission_classes", [])

        if not hasattr(permissions, "__iter__"):
            permissions = [permissions]

        return permissions

    def has_permission(self, request, view):
        """
        Check the permissions on the view.
        """

        permissions = self.get_permissions(view)

        if not permissions:
            return False

        for perm_class in permissions:
            if hasattr(perm_class, "__iter__"):
                classes = perm_class

                for perm_class in classes:
                    permission = perm_class()

                    if permission.has_permission(request, view):
                        break
                    else:
                        return False
            else:
                permission = perm_class()

                if permission.has_permission(request, view):
                    return True

        return False

    def has_object_permission(self, request, view, obj):
        """
        Check the object permissions on the view.
        """

        permissions = self.get_permissions(view)

        if not permissions:
            return False

        for perm_class in permissions:
            if hasattr(perm_class, "__iter__"):
                classes = perm_class

                for perm_class in classes:
                    permission = perm_class()

                    if permission.has_object_permission(request, view, obj):
                        break
                    else:
                        return False
            else:
                permission = perm_class()

                if permission.has_object_permission(request, view, obj):
                    return True

        return False


