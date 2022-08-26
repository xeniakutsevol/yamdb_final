from rest_framework import permissions


class UsersPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        role = request.data.get('role')
        return request.user.is_admin or role is None


class ReviewCommentPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user
            and request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (request.user and request.user.is_authenticated
                and (request.user.is_staff
                     or request.user.is_admin
                     or request.user.is_moderator
                     or obj.author == request.user
                     or request.method == 'POST'
                     and request.user.is_authenticated)
                or request.method in permissions.SAFE_METHODS)


class IsAdminUserOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or (request.user.is_authenticated and request.user.is_admin))


class IsAdminOrSuperuser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.is_admin
                                                  or request.user.is_superuser)
