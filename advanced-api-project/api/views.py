"""
API Views for the Book model using Django REST Framework generic views.

This module contains all the API views for handling CRUD operations on the Book model.
It implements Django REST Framework's generic views to provide a consistent and
efficient API interface with built-in functionality for common operations.

Views included:
- BookListView: Handles listing all books (GET)
- BookDetailView: Handles retrieving a single book (GET)
- BookCreateView: Handles creating new books (POST)
- BookUpdateView: Handles updating existing books (PUT/PATCH)
- BookDeleteView: Handles deleting books (DELETE)

All views include proper permissions, serializers, and custom behavior
as needed for the specific use case.
"""

from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import Book, Author
from .serializers import BookSerializer
from .permissions import IsAuthenticatedOrReadOnly, IsAdminOrReadOnly


class BookListView(generics.ListAPIView):
    """
    API view for listing all books.
    
    This view handles GET requests to retrieve a list of all books in the system.
    It supports filtering, searching, and ordering of results through query parameters.
    
    Features:
    - Read-only access (no authentication required)
    - Supports filtering by publication year and author
    - Supports searching in book titles and author names
    - Supports ordering by title and publication year
    - Paginated results for better performance
    
    Endpoints:
    - GET /api/books/ : Returns list of all books
    
    Query Parameters:
    - publication_year: Filter books by publication year
    - author: Filter books by author ID
    - search: Search in book titles and author names
    - ordering: Order results (title, -title, publication_year, -publication_year)
    """
    queryset = Book.objects.all().select_related('author')
    serializer_class = BookSerializer
    permission_classes = [permissions.AllowAny]  # Allow read access to everyone
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['publication_year', 'author']
    search_fields = ['title', 'author__name']  # Allow searching by book title and author name
    ordering_fields = ['title', 'publication_year']
    ordering = ['-publication_year', 'title']  # Default ordering


class BookDetailView(generics.RetrieveAPIView):
    """
    API view for retrieving a single book by ID.
    
    This view handles GET requests to retrieve detailed information about
    a specific book identified by its primary key (ID).
    
    Features:
    - Read-only access (no authentication required)
    - Returns 404 if book doesn't exist
    - Includes related author information
    
    Endpoints:
    - GET /api/books/{id}/ : Returns details of a specific book
    """
    queryset = Book.objects.all().select_related('author')
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]  # Allow read access to everyone


class BookCreateView(generics.CreateAPIView):
    """
    API view for creating new books.
    
    This view handles POST requests to create new book instances in the system.
    Only authenticated users are allowed to create books.
    
    Features:
    - Requires authentication (authenticated users only)
    - Validates data using BookSerializer
    - Returns created book data with 201 status
    - Custom validation for publication year
    - Prevents duplicate books by the same author
    - Uses database transactions for data integrity
    
    Endpoints:
    - POST /api/books/create/ : Creates a new book
    
    Required fields:
    - title: Book title (max 200 characters)
    - publication_year: Year of publication (not in future)
    - author: ID of existing author
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]  # Only authenticated users can create
    
    def perform_create(self, serializer):
        """
        Custom create logic to handle additional processing during book creation.
        
        This method is called after validation but before saving the instance.
        It implements transaction safety and additional business logic validation.
        
        Args:
            serializer: The validated serializer instance
            
        Raises:
            ValidationError: If duplicate book is detected or other validation fails
        """
        validated_data = serializer.validated_data
        title = validated_data.get('title')
        author = validated_data.get('author')
        publication_year = validated_data.get('publication_year')
        
        # Check for duplicate books by the same author with same title and year
        if Book.objects.filter(
            title__iexact=title,  # Case-insensitive comparison
            author=author,
            publication_year=publication_year
        ).exists():
            raise ValidationError(
                f"A book with title '{title}' by {author.name} "
                f"published in {publication_year} already exists."
            )
        
        # Use database transaction to ensure data consistency
        with transaction.atomic():
            # Log the creation attempt (in a real app, you might want proper logging)
            print(f"Creating new book: {title} by {author.name} ({publication_year})")
            
            # Save the book instance
            book = serializer.save()
            
            # You could add additional post-creation logic here
            # For example: sending notifications, updating related models, etc.
            print(f"Successfully created book with ID: {book.id}")
            
            return book


class BookUpdateView(generics.UpdateAPIView):
    """
    API view for updating existing books.
    
    This view handles PUT and PATCH requests to update existing book instances.
    Only authenticated users are allowed to update books.
    
    Features:
    - Requires authentication (authenticated users only)
    - Supports both full updates (PUT) and partial updates (PATCH)
    - Validates data using BookSerializer
    - Returns updated book data
    - Prevents duplicate books during updates
    - Uses database transactions for data integrity
    
    Endpoints:
    - PUT /api/books/{id}/update/ : Full update of a book
    - PATCH /api/books/{id}/update/ : Partial update of a book
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]  # Only authenticated users can update
    
    def perform_update(self, serializer):
        """
        Custom update logic to handle additional processing during book updates.
        
        This method is called after validation but before saving the updated instance.
        It implements duplicate checking and transaction safety.
        
        Args:
            serializer: The validated serializer instance
            
        Raises:
            ValidationError: If duplicate book is detected during update
        """
        instance = serializer.instance
        validated_data = serializer.validated_data
        
        # Get the new values (or keep existing ones for partial updates)
        new_title = validated_data.get('title', instance.title)
        new_author = validated_data.get('author', instance.author)
        new_publication_year = validated_data.get('publication_year', instance.publication_year)
        
        # Check for duplicate books (excluding the current instance)
        duplicate_exists = Book.objects.filter(
            title__iexact=new_title,
            author=new_author,
            publication_year=new_publication_year
        ).exclude(id=instance.id).exists()
        
        if duplicate_exists:
            raise ValidationError(
                f"A book with title '{new_title}' by {new_author.name} "
                f"published in {new_publication_year} already exists."
            )
        
        # Use database transaction to ensure data consistency
        with transaction.atomic():
            # Log the update attempt
            print(f"Updating book: {instance.title} (ID: {instance.id})")
            
            # Save the updated book instance
            updated_book = serializer.save()
            
            # Log successful update
            print(f"Successfully updated book: {updated_book.title}")
            
            return updated_book


class BookDeleteView(generics.DestroyAPIView):
    """
    API view for deleting books.
    
    This view handles DELETE requests to remove existing book instances from the system.
    Only authenticated users are allowed to delete books.
    
    Features:
    - Requires authentication (authenticated users only)
    - Returns 204 No Content on successful deletion
    - Returns 404 if book doesn't exist
    - Soft delete could be implemented here if needed
    
    Endpoints:
    - DELETE /api/books/{id}/delete/ : Deletes a specific book
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAdminOrReadOnly]  # Only admin users can delete books
    
    def perform_destroy(self, instance):
        """
        Custom delete logic to handle additional processing during book deletion.
        
        This method is called before the instance is deleted from the database.
        It can be used to add logging, cleanup, or implement soft delete functionality.
        
        Args:
            instance: The book instance to be deleted
        """
        # Log the deletion attempt
        print(f"Deleting book: {instance.title}")
        
        # Perform the actual deletion
        instance.delete()
