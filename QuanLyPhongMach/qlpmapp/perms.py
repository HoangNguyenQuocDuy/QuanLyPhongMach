from django.contrib.auth.models import Group
from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied
from qlpmapp.models import User, Administrator, Patient, Nurse, Doctor


class AdminPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            admin = Administrator.objects.get(user=request.user)
            if not admin.groups.filter(name='Admin').exists():
                raise PermissionDenied()
        except Administrator.DoesNotExist:
            raise PermissionDenied()
        return True


class PatientPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            user = Patient.objects.get(user=request.user)
            if not user.groups.filter(name='Patient').exists():
                raise PermissionDenied()
        except Patient.DoesNotExist:
            raise PermissionDenied()
        return True


class NursePermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            nurse = Nurse.objects.get(user=request.user)
            if not nurse.groups.filter(name='Nurse').exists():
                raise PermissionDenied()
        except Nurse.DoesNotExist:
            raise PermissionDenied()
        return True


class DoctorPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            doctor = Doctor.objects.get(user=request.user)
            if not doctor.groups.filter(name='Doctor').exists():
                raise PermissionDenied()
        except Doctor.DoesNotExist:
            raise PermissionDenied()
        return True
