"""
Custom permission classes for the API app.

This module defines custom permission classes that extend Django REST Framework's
base permission system to provide more granular control over API access.

Permission Classes:
- IsOwnerOrReadOnly: Allows read access to everyone, but write access only to owners
- IsAuthenticatedOrReadOnly: Allows read access to everyone, write access to authenticated users
"""

from rest_framework import permissions


class IsAuthenticatedOrReadOnly(permissions.BasePermission):
    """
    Custom permission class that allows:
    - Read permissions (GET, HEAD, OPTIONS) to any user (authenticated or not)
    - Write permissions (POST, PUT, PATCH, DELETE) only to authenticated users
    
    This is useful for APIs where you want public read access but require
    authentication for any modifications.
    """
    
    def has_permission(self, request, view):
        """
        Check if the user has permission to access the view.
        
        Args:
            request: The HTTP request object
            view: The view being accessed
            
        Returns:
            bool: True if permission is granted, False otherwise
        """
        # Read permissions are allowed for any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Write permissions are only allowed to authenticated users.
        return request.user and request.user.is_authenticated


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission class that allows:
    - Read permissions to any user
    - Write permissions only to the owner of the object
    
    Note: This assumes the model has a 'created_by' or 'owner' field.
    For the Book model, this would require adding such a field.
    """
    
    def has_permission(self, request, view):
        """
        Check if the user has permission to access the view.
        """
        # Read permissions are allowed for any request
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Write permissions require authentication
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """
        Check if the user has permission to access the specific object.
        
        Args:
            request: The HTTP request object
            view: The view being accessed
            obj: The model instance being accessed
            
        Returns:
            bool: True if permission is granted, False otherwise
        """
        # Read permissions are allowed for any request
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Write permissions are only allowed to the owner of the object
        # Note: This assumes the model has a 'created_by' field
        # For now, we'll allow any authenticated user since Book model
        # doesn't have ownership tracking
        return request.user and request.user.is_authenticated


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission class that allows:
    - Read permissions to any user
    - Write permissions only to admin users (is_staff=True)
    
    This is useful for content that should be publicly readable but only
    modifiable by administrators.
    """
    
    def has_permission(self, request, view):
        """
        Check if the user has permission to access the view.
        """
        # Read permissions are allowed for any request
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Write permissions are only allowed to admin users
        return request.user and request.user.is_authenticated and request.user.is_staff