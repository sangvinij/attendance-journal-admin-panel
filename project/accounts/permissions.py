from rest_framework.permissions import BasePermission, IsAuthenticated, SAFE_METHODS


class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)


class CurrentUserOrSuperUser(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        user = request.user
        if obj == user:
            return True
        return request.method in SAFE_METHODS or user.is_superuser
