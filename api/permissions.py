from rest_framework import permissions


class IsModerator(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role == "moderator"

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsStaff(permissions.IsAdminUser):
    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsStaffOrReadOnly(IsStaff):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return super().has_permission(request, view)


class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user
