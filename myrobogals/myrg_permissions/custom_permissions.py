from django.test import TestCase
from django.test.client import RequestFactory
from rest_framework.permissions import BasePermission
from rest_framework.views import APIView
# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

        
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


class IsAdminRobogals(BasePermission):
    
    #def get_object(self):
     #   obj = get_object_or_404(self.get_queryset())
      #  logger.error(obj)
       # self.check_object_permissions(self.request, obj)
        #return obj
    
    def has_permission(self, request, view):
        from myrg_groups.serializers import RoleSerializer
        from myrg_groups.models import Role
        logger.error("view_permission")
        user_obj = request.user
        logger.error(user_obj.id)
        #select all user_id based on roles e.g superadmin, robogals admin, software team
        role_query = Role.objects.filter(role_class="1")
        role_serializer = RoleSerializer
        role_serializer.Meta.fields = ("user",)
        role_serializer_query = role_serializer(role_query, many=True)
        logger.error(role_serializer_query.data)
        data = json.loads(role_serializer_query.data)
        role_list = data.get("user")
        logger.error(role_list)
        if user_obj.id in role_serializer_query.data.user:
             return True
        #Slogger.error(role_serializer_query.data)
        #return True
        
    def has_object_permission(self, request, view, obj):
        logger.error("obj_permission")
        return True

class IsTeamMember(BasePermission):
    
    def has_permission(self, request, view):
        from myrg_groups.serializers import RoleSerializer
        from myrg_groups.models import Role
        #logger.error(request.META['REMOTE_ADDR'])
        user_obj = request.user
        # check role_class based on user_id
        #logger.error(user_obj.role_set.filter(user=user_obj.id))
        #logger.error(Role.objects.filter(user=user_obj.id))
        
        
        role_query = user_obj.role_set.filter(user=user_obj.id)
        
        role_serializer = RoleSerializer
        role_serializer.Meta.fields = ("id","group","role_class",)        
        role_serializer_query = role_serializer(role_query, many=True)
        #Slogger.error(role_serializer_query.data)
        if role_id is None:
            return False
            
        try:
            role_id = smart_text(role_id)
            role_query = user_obj.role_set.filter(Q(date_start__lte=timezone.now()) & (Q(date_end__isnull=True) | Q(date_end__gte=timezone.now()))).get(pk = role_id)
                    
            request.session['role_id'] = role_id
                    
            return True
        except:
            return False
        
        #ip_addr = request.META['REMOTE_ADDR']
        #blacklisted = Blacklist.objects.filter(ip_addr=ip_addr).exists()
        #return not blacklisted
        
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:            
            return True

        # Instance must have an attribute named `owner`.
        return obj.owner == request.user
        
class IsPublicUser(BasePermission):
    
    def has_permission(self, request, view):
        return False
        

# example from https://github.com/caxap/rest_condition

class IsOwnerOrReadOnly(BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Instance must have an attribute named `owner`.
        return obj.owner == request.user
        
class IsLucky(BasePermission):

    def has_permission(self, request, view):
        import random
        
        return random.randint(1, 10) > 8


class TestView(APIView):

    def test_permission(self, request):
        from rest_framework.request import Request

        request = Request(request)

        self.request = request

        for permission in self.get_permissions():
            if not permission.has_permission(request, self):
                return False

        return True


class TruePermission(BasePermission):

    def has_permission(self, request, view):
        return True


class FalsePermission(BasePermission):

    def has_permission(self, request, view):
        return False


class PermissionsTest(TestCase):

    def setUp(self):
        self.requests = RequestFactory()

    def test_no_permissions(self):
        class DefaultApiView(TestView):
            permission_classes = [AnyPermissions]

        view = DefaultApiView()
        request = self.requests.get("/")

        self.assertFalse(view.test_permission(request))

    def test_single_permission_flat(self):
        class DefaultApiView(TestView):
            permission_classes = [AnyPermissions]
            any_permission_classes = TruePermission

        view = DefaultApiView()
        request = self.requests.get("/")

        self.assertTrue(view.test_permission(request))

    def test_single_permission_passed(self):
        class DefaultApiView(TestView):
            permission_classes = [AnyPermissions]
            any_permission_classes = [TruePermission]

        view = DefaultApiView()
        request = self.requests.get("/")

        self.assertTrue(view.test_permission(request))

    def test_single_permission_failed(self):
        class DefaultApiView(TestView):
            permission_classes = [AnyPermissions]
            any_permission_classes = [FalsePermission]

        view = DefaultApiView()
        request = self.requests.get("/")

        self.assertFalse(view.test_permission(request))

    def test_multiple_permissions_passed(self):
        class DefaultApiView(TestView):
            permission_classes = [AnyPermissions]
            any_permission_classes = [TruePermission, FalsePermission]

        view = DefaultApiView()
        request = self.requests.get("/")

        self.assertTrue(view.test_permission(request))

    def test_multiple_permissions_passed_any_order(self):
        class DefaultApiView(TestView):
            permission_classes = [AnyPermissions]
            any_permission_classes = [FalsePermission, TruePermission]

        view = DefaultApiView()
        request = self.requests.get("/")

        self.assertTrue(view.test_permission(request))

    def test_multiple_permissions_failed(self):
        class DefaultApiView(TestView):
            permission_classes = [AnyPermissions]
            any_permission_classes = [FalsePermission, FalsePermission]

        view = DefaultApiView()
        request = self.requests.get("/")

        self.assertFalse(view.test_permission(request))

    def test_chained_permissions(self):
        class DefaultApiView(TestView):
            permission_classes = [AnyPermissions]
            any_permission_classes = [
                [TruePermission, FalsePermission],
                TruePermission,
            ]

        view = DefaultApiView()
        request = self.requests.get("/")

        self.assertTrue(view.test_permission(request))

    def test_chained_first_failed(self):
        class DefaultApiView(TestView):
            permission_classes = [AnyPermissions]
            any_permission_classes = [
                FalsePermission,
                [TruePermission, FalsePermission],
            ]

        view = DefaultApiView()
        request = self.requests.get("/")

        self.assertFalse(view.test_permission(request))

    def test_chained_late_failed(self):
        class DefaultApiView(TestView):
            permission_classes = [AnyPermissions]
            any_permission_classes = [
                [TruePermission, FalsePermission],
                FalsePermission,
            ]

        view = DefaultApiView()
        request = self.requests.get("/")

        self.assertFalse(view.test_permission(request))
