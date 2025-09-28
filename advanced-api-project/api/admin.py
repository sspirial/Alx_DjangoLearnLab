from django.contrib import admin
from .models import Author, Book


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    """
    Admin interface configuration for Author model.
    
    Provides a user-friendly interface for managing authors in Django admin,
    including list display, search functionality, and related book management.
    """
    list_display = ['id', 'name', 'books_count']
    list_display_links = ['id', 'name']
    search_fields = ['name']
    ordering = ['name']
    
    def books_count(self, obj):
        """Display the number of books by this author."""
        return obj.books.count()
    books_count.short_description = 'Number of Books'


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """
    Admin interface configuration for Book model.
    
    Provides comprehensive management for books including filtering,
    search capabilities, and proper display of relationships.
    """
    list_display = ['id', 'title', 'author', 'publication_year']
    list_display_links = ['id', 'title']
    list_filter = ['publication_year', 'author']
    search_fields = ['title', 'author__name']
    ordering = ['-publication_year', 'title']
    
    # Group fields in the form
    fieldsets = (
        ('Book Information', {
            'fields': ('title', 'publication_year')
        }),
        ('Relationship', {
            'fields': ('author',)
        })
    )
