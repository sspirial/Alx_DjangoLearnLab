from django.shortcuts import render
from rest_framework import generics, viewsets, permissions
from .models import Book
from .serializers import BookSerializer

# Create your views here.

class BookList(generics.ListAPIView):
    """
    API view to retrieve a list of all books.
    Uses BookSerializer to convert Book model instances to JSON.
    
    Permissions: Allow any user (authenticated or not) to view the book list.
    This provides a public read-only endpoint for browsing books.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.AllowAny]  # Public read access


class BookViewSet(viewsets.ModelViewSet):
    """
    ViewSet that provides default CRUD operations for the Book model.
    
    This ViewSet automatically provides the following actions:
    - list: GET /books_all/ - List all books
    - create: POST /books_all/ - Create a new book
    - retrieve: GET /books_all/<id>/ - Retrieve a specific book
    - update: PUT /books_all/<id>/ - Update a specific book
    - partial_update: PATCH /books_all/<id>/ - Partially update a specific book
    - destroy: DELETE /books_all/<id>/ - Delete a specific book
    
    Permissions: Requires authentication for all operations.
    Users must provide a valid token to access any of these endpoints.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]  # Requires authentication for all CRUD operations
