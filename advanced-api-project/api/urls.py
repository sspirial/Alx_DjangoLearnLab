"""
URL configuration for the api app.

This module defines the URL patterns for the API endpoints, routing
different URLs to their corresponding view classes for CRUD operations
on the Book model.

URL Patterns:
- books/ : ListView for all books (GET)
- books/<int:pk>/ : DetailView for a specific book (GET)
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
    # Returns a list of all books in the system
    path('books/', views.BookListView.as_view(), name='book-list'),
    
    # Book DetailView - GET /api/books/<id>/
    # Returns detailed information about a specific book
    path('books/<int:pk>/', views.BookDetailView.as_view(), name='book-detail'),
    
    # Book CreateView - POST /api/books/create/
    # Creates a new book instance
    path('books/create/', views.BookCreateView.as_view(), name='book-create'),
    
    # Book UpdateView - PUT/PATCH /api/books/<id>/update/
    # Updates an existing book instance
    path('books/<int:pk>/update/', views.BookUpdateView.as_view(), name='book-update'),
    
    # Book DeleteView - DELETE /api/books/<id>/delete/
    # Deletes an existing book instance
    path('books/<int:pk>/delete/', views.BookDeleteView.as_view(), name='book-delete'),
]