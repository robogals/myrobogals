from .models import PermissionDefinition

def get_permission(role):
    pd = PermissionDefinition.objects.get(role_class=role)
    return pd.definition
