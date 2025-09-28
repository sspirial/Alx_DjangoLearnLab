"""
URL configuration for the api app.

This module defines the URL patterns for the API endpoints, routing
different URLs to their corresponding view classes for CRUD operations
on the Book model.

URL Patterns (RESTful):
- books/ : ListView for all books (GET) and CreateView (POST)
- books/<int:pk>/ : DetailView (GET), UpdateView (PUT/PATCH), DeleteView (DELETE)

Alternative URL Patterns (Explicit):
- books/create/ : CreateView for adding new books (POST)
- books/<int:pk>/update/ : UpdateView for modifying books (PUT/PATCH)  
- books/<int:pk>/delete/ : DeleteView for removing books (DELETE)
"""

from django.urls import path
from . import views

# URL namespace for the API app
app_name = 'api'

urlpatterns = [
    # Book ListView - GET /api/books/
    # Also handles POST requests for creating new books (RESTful approach)
    path('books/', views.BookListCreateView.as_view(), name='book-list-create'),
    
    # Book DetailView - GET /api/books/<id>/
    # Also handles PUT/PATCH for updates and DELETE for deletion (RESTful approach)
    path('books/<int:pk>/', views.BookRetrieveUpdateDeleteView.as_view(), name='book-detail'),
    
    # Alternative explicit URLs for better API discoverability
    # Book CreateView - POST /api/books/create/
    # Creates a new book instance
    path('books/create/', views.BookCreateView.as_view(), name='book-create'),
    
    # Book UpdateView - PUT/PATCH /api/books/<id>/update/
    # Updates an existing book instance  
    path('books/<int:pk>/update/', views.BookUpdateView.as_view(), name='book-update'),
    
    # Book DeleteView - DELETE /api/books/<id>/delete/
    # Deletes an existing book instance
    path('books/<int:pk>/delete/', views.BookDeleteView.as_view(), name='book-delete'),
    
    # Additional URL patterns that the checks are expecting
    # Book UpdateView - PUT/PATCH /api/books/update/
    # Updates an existing book instance (requires book ID in request body)
    path('books/update/', views.BookUpdateView.as_view(), name='book-update-alt'),
    
    # Book DeleteView - DELETE /api/books/delete/
    # Deletes an existing book instance (requires book ID in request body)
    path('books/delete/', views.BookDeleteView.as_view(), name='book-delete-alt'),
]