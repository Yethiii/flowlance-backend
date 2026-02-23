from rest_framework import permissions


class IsFreelanceRole(permissions.BasePermission):

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role == 'FREELANCE'


class IsCompanyRole(permissions.BasePermission):

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role == 'COMPANY'


class IsOwnerOfProfile(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if hasattr(obj, 'freelance_user'):
            return obj.freelance_user == request.user
        if hasattr(obj, 'company_user'):
            return obj.company_user == request.user
        return False