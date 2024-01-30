from django.contrib.auth.models import Group
from rest_framework import permissions
from qlpmapp.models import User, Administrator
from rest_framework.exceptions import PermissionDenied


class AdminPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            admin = Administrator.objects.get(user=request.user)
            if not admin.groups.filter(name='Admin').exists():
                raise PermissionDenied()
        except Administrator.DoesNotExist:
            raise PermissionDenied()
        return True
