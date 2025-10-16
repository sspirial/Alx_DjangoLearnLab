"""Custom permission classes for post and comment resources."""

from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrReadOnly(BasePermission):
    """Allow object modification only for the author of the resource."""

    message = "You can only modify content that you created."

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        author = getattr(obj, "author", None)
        if author is None:
            return False

        return author == request.user
