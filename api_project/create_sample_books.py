#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api_project.settings')
sys.path.append('/c/Users/emmun/projects/Alx_DjangoLearnLab/api_project')
django.setup()

from api.models import Book

# Create some sample books
books_data = [
    {"title": "The Great Gatsby", "author": "F. Scott Fitzgerald"},
    {"title": "To Kill a Mockingbird", "author": "Harper Lee"},
    {"title": "1984", "author": "George Orwell"},
    {"title": "Pride and Prejudice", "author": "Jane Austen"},
    {"title": "The Catcher in the Rye", "author": "J.D. Salinger"}
]

# Clear existing books to avoid duplicates
Book.objects.all().delete()

# Create new books
for book_data in books_data:
    book = Book.objects.create(**book_data)
    print(f"Created book: {book}")

print(f"\nTotal books in database: {Book.objects.count()}")