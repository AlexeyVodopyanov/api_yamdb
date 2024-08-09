from rest_framework.permissions import SAFE_METHODS, BasePermission

from reviews.models import User


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated
                and (request.user.role == User.Role.ADMIN
                     or request.user.is_superuser))


class IsModerator(BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated
                and request.user.role == User.Role.MODERATOR)


class IsAuthorOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (request.method in SAFE_METHODS
                or obj.author == request.user)


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or (request.user.is_authenticated
                and (request.user.role == User.Role.ADMIN
                     or request.user.is_superuser))
        )


class IsAuthorOrModeratorOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if (request.method in SAFE_METHODS
                or request.user.is_authenticated):
            return True
        return (request.user.is_authenticated
                and (request.user.role
                     in (User.Role.MODERATOR, User.Role.ADMIN)
                     or request.user.is_superuser))

    def has_object_permission(self, request, view, obj):
        if (request.method in SAFE_METHODS
                or obj.author == request.user):
            return True
        return (request.user.is_authenticated
                and (request.user.role
                     in (User.Role.MODERATOR, User.Role.ADMIN)
                     or request.user.is_superuser))
