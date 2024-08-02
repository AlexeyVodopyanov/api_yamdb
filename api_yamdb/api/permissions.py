from rest_framework.permissions import BasePermission, SAFE_METHODS


MODER_ADMIN = ('moderator', 'Moderator', 'admin', 'Admin')

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


class IsModerator(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'moderator'


class IsAuthorOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.author == request.user


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or (request.user.is_authenticated and request.user.role == 'admin')
        )


class IsAuthorOrModeratorOrReadOnly(BasePermission):

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS or request.user and request.user.is_authenticated:
            return True
        if request.user.is_authenticated:
            return (request.user.role in MODER_ADMIN)
        return False

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if request.user.is_authenticated:
            if request.user.role in MODER_ADMIN:
                return True
        if obj.author == request.user:
            return True
        return False
