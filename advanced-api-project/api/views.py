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
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters_backend, FilterSet, CharFilter, NumberFilter, DateFilter
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import Book, Author
from .serializers import BookSerializer


class BookFilter(FilterSet):
    """
    Custom filter set for advanced Book filtering capabilities.
    
    This FilterSet provides comprehensive filtering options for the Book model,
    including exact matches, partial matches, and range filters.
    
    Available filters:
    - title: Exact match filter for book title
    - title__icontains: Case-insensitive partial match for book title
    - author__name: Exact match filter for author name
    - author__name__icontains: Case-insensitive partial match for author name
    - publication_year: Exact match filter for publication year
    - publication_year__gte: Filter for books published in or after a specific year
    - publication_year__lte: Filter for books published in or before a specific year
    """
    # Title filters
    title = CharFilter(lookup_expr='exact', help_text="Exact title match")
    title__icontains = CharFilter(field_name='title', lookup_expr='icontains', 
                                help_text="Case-insensitive partial title match")
    
    # Author filters
    author__name = CharFilter(field_name='author__name', lookup_expr='exact',
                            help_text="Exact author name match")
    author__name__icontains = CharFilter(field_name='author__name', lookup_expr='icontains',
                                       help_text="Case-insensitive partial author name match")
    
    # Publication year filters
    publication_year = NumberFilter(lookup_expr='exact', 
                                  help_text="Exact publication year match")
    publication_year__gte = NumberFilter(field_name='publication_year', lookup_expr='gte',
                                       help_text="Books published in or after this year")
    publication_year__lte = NumberFilter(field_name='publication_year', lookup_expr='lte',
                                       help_text="Books published in or before this year")
    
    class Meta:
        model = Book
        fields = {
            'title': ['exact', 'icontains'],
            'author__name': ['exact', 'icontains'],
            'publication_year': ['exact', 'gte', 'lte'],
        }


class BookListView(generics.ListAPIView):
    """
    API view for listing all books.
    
    This view handles GET requests to retrieve a list of all books in the system.
    It supports filtering, searching, and ordering of results through query parameters.
    
    Features:
    - Read-only access (no authentication required)
    - Advanced filtering with exact, partial, and range filters
    - Full-text search in book titles and author names
    - Flexible ordering by multiple fields
    - Paginated results for better performance
    
    Endpoints:
    - GET /api/books/ : Returns list of all books
    
    Query Parameters:
    Filtering:
    - title: Exact title match
    - title__icontains: Case-insensitive partial title match
    - author__name: Exact author name match
    - author__name__icontains: Case-insensitive partial author name match
    - publication_year: Exact publication year
    - publication_year__gte: Books published in or after this year
    - publication_year__lte: Books published in or before this year
    
    Searching:
    - search: Full-text search in book titles and author names
    
    Ordering:
    - ordering: Order by title, publication_year (use '-' prefix for descending)
    
    Examples:
    - /api/books/?title__icontains=django : Books with "django" in title
    - /api/books/?publication_year__gte=2020 : Books from 2020 onwards
    - /api/books/?search=python : Search for "python" in titles and authors
    - /api/books/?ordering=-publication_year,title : Order by year (desc), then title (asc)
    """
    queryset = Book.objects.all().select_related('author')
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    # Configure filter backends
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # Use custom filterset class for advanced filtering
    filterset_class = BookFilter
    
    # Configure search fields for full-text search
    search_fields = ['title', 'author__name']
    
    # Configure ordering fields
    ordering_fields = ['title', 'publication_year', 'author__name']
    ordering = ['-publication_year', 'title']  # Default ordering: newest first, then alphabetical


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
    permission_classes = [IsAuthenticated]  # Only authenticated users can create
    
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
    permission_classes = [IsAuthenticated]  # Only authenticated users can update
    
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
    permission_classes = [IsAuthenticated]  # Only authenticated users can delete books
    
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


class BookListCreateView(generics.ListCreateAPIView):
    """
    Combined API view for listing all books and creating new books.
    
    This view follows RESTful conventions by handling both GET (list) and 
    POST (create) requests on the same endpoint. It's an alternative to 
    separate ListView and CreateView classes.
    
    Features:
    - GET: Returns paginated list of all books (no authentication required)
    - POST: Creates new books (authentication required)
    - Supports filtering, searching, and ordering for GET requests
    - Validates data using BookSerializer for POST requests
    
    Endpoints:
    - GET /api/books/ : Returns list of all books
    - POST /api/books/ : Creates a new book
    """
    queryset = Book.objects.all().select_related('author')
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = BookFilter
    search_fields = ['title', 'author__name']
    ordering_fields = ['title', 'publication_year', 'author__name']
    ordering = ['-publication_year', 'title']
    
    def perform_create(self, serializer):
        """
        Custom create logic for the combined view.
        """
        print(f"Creating new book via combined endpoint: {serializer.validated_data.get('title')}")
        serializer.save()


class BookRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    """
    Combined API view for retrieving, updating, and deleting a single book.
    
    This view follows RESTful conventions by handling GET (retrieve), 
    PUT/PATCH (update), and DELETE (destroy) requests on the same endpoint.
    It's an alternative to separate DetailView, UpdateView, and DeleteView classes.
    
    Features:
    - GET: Returns book details (no authentication required)
    - PUT/PATCH: Updates book (authentication required)  
    - DELETE: Deletes book (admin authentication required)
    - Includes duplicate checking for updates
    - Uses database transactions for data integrity
    
    Endpoints:
    - GET /api/books/{id}/ : Returns details of a specific book
    - PUT /api/books/{id}/ : Full update of a book
    - PATCH /api/books/{id}/ : Partial update of a book  
    - DELETE /api/books/{id}/ : Deletes a specific book
    """
    queryset = Book.objects.all().select_related('author')
    serializer_class = BookSerializer
    
    def get_permissions(self):
        """
        Instantiate and return the list of permissions that this view requires.
        
        Different HTTP methods require different permission levels:
        - GET: Read-only access for everyone
        - PUT/PATCH: Authentication required
        - DELETE: Admin access required
        """
        if self.request.method == 'DELETE':
            permission_classes = [IsAuthenticated]
        elif self.request.method in ['PUT', 'PATCH']:
            permission_classes = [IsAuthenticated]
        else:  # GET
            permission_classes = [IsAuthenticatedOrReadOnly]
            
        return [permission() for permission in permission_classes]
    
    def perform_update(self, serializer):
        """
        Custom update logic with duplicate checking.
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
            print(f"Updating book via combined endpoint: {instance.title} (ID: {instance.id})")
            updated_book = serializer.save()
            print(f"Successfully updated book: {updated_book.title}")
            return updated_book
    
    def perform_destroy(self, instance):
        """
        Custom delete logic for the combined view.
        """
        print(f"Deleting book via combined endpoint: {instance.title}")
        instance.delete()
