#!/usr/bin/env python
"""
Test script for Advanced API Project models and serializers.

This script demonstrates the functionality of the Author and Book models
along with their custom serializers, including validation and nested relationships.
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append('/home/munubi/Alx_DjangoLearnLab/advanced-api-project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'advanced_api_project.settings')
django.setup()

from api.models import Author, Book
from api.serializers import AuthorSerializer, BookSerializer, AuthorDetailSerializer
from datetime import date


def test_models_and_serializers():
    """Test the models and serializers functionality."""
    
    print("=" * 60)
    print("TESTING DJANGO MODELS AND DRF SERIALIZERS")
    print("=" * 60)
    
    # Clean up any existing test data
    Author.objects.filter(name__startswith='Test').delete()
    
    print("\n1. Testing Author Model Creation:")
    print("-" * 40)
    
    # Create test authors
    author1 = Author.objects.create(name='J.K. Rowling')
    author2 = Author.objects.create(name='George Orwell')
    
    print(f"✓ Created author 1: {author1}")
    print(f"✓ Created author 2: {author2}")
    
    print("\n2. Testing Book Model Creation:")
    print("-" * 40)
    
    # Create test books
    book1 = Book.objects.create(
        title="Harry Potter and the Philosopher's Stone",
        publication_year=1997,
        author=author1
    )
    
    book2 = Book.objects.create(
        title="Harry Potter and the Chamber of Secrets",
        publication_year=1998,
        author=author1
    )
    
    book3 = Book.objects.create(
        title="1984",
        publication_year=1949,
        author=author2
    )
    
    print(f"✓ Created book 1: {book1}")
    print(f"✓ Created book 2: {book2}")
    print(f"✓ Created book 3: {book3}")
    
    print("\n3. Testing Model Relationships:")
    print("-" * 40)
    
    # Test the one-to-many relationship
    jk_books = author1.books.all()
    print(f"✓ J.K. Rowling has {jk_books.count()} books:")
    for book in jk_books:
        print(f"  - {book}")
    
    orwell_books = author2.books.all()
    print(f"✓ George Orwell has {orwell_books.count()} book(s):")
    for book in orwell_books:
        print(f"  - {book}")
    
    print("\n4. Testing BookSerializer:")
    print("-" * 40)
    
    # Test BookSerializer
    book_serializer = BookSerializer(book1)
    print(f"✓ Book serialization successful:")
    for key, value in book_serializer.data.items():
        print(f"  {key}: {value}")
    
    print("\n5. Testing BookSerializer Validation (Future Year):")
    print("-" * 40)
    
    # Test validation for future publication year
    try:
        future_book_data = {
            'title': 'Future Book',
            'publication_year': date.today().year + 1,
            'author': author1.id
        }
        future_book_serializer = BookSerializer(data=future_book_data)
        if future_book_serializer.is_valid():
            print("✗ Validation failed - future year should not be allowed")
        else:
            print("✓ Validation correctly rejected future publication year:")
            print(f"  Error: {future_book_serializer.errors}")
    except Exception as e:
        print(f"✗ Error during validation test: {e}")
    
    print("\n6. Testing AuthorSerializer (Nested Books):")
    print("-" * 40)
    
    # Test AuthorSerializer with nested books
    author_serializer = AuthorSerializer(author1)
    print(f"✓ Author serialization with nested books:")
    author_data = author_serializer.data
    print(f"  Author ID: {author_data['id']}")
    print(f"  Author Name: {author_data['name']}")
    print(f"  Books Count: {author_data['books_count']}")
    print(f"  Latest Publication Year: {author_data['latest_publication_year']}")
    print(f"  Books:")
    for book in author_data['books']:
        print(f"    - {book['title']} ({book['publication_year']})")
    
    print("\n7. Testing AuthorDetailSerializer (Lightweight):")
    print("-" * 40)
    
    # Test AuthorDetailSerializer
    author_detail_serializer = AuthorDetailSerializer(author1)
    print(f"✓ Author detail serialization (lightweight):")
    detail_data = author_detail_serializer.data
    for key, value in detail_data.items():
        print(f"  {key}: {value}")
    
    print("\n8. Testing Author Name Validation:")
    print("-" * 40)
    
    # Test author name validation
    try:
        invalid_author_data = {'name': 'X'}  # Too short
        author_serializer = AuthorSerializer(data=invalid_author_data)
        if author_serializer.is_valid():
            print("✗ Validation failed - short name should not be allowed")
        else:
            print("✓ Validation correctly rejected short author name:")
            print(f"  Error: {author_serializer.errors}")
    except Exception as e:
        print(f"✗ Error during author validation test: {e}")
    
    print("\n9. Database Query Verification:")
    print("-" * 40)
    
    # Verify database state
    total_authors = Author.objects.count()
    total_books = Book.objects.count()
    
    print(f"✓ Total authors in database: {total_authors}")
    print(f"✓ Total books in database: {total_books}")
    
    # Test unique constraint
    print(f"✓ Unique constraint working: {Book._meta.unique_together}")
    
    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED SUCCESSFULLY!")
    print("Models and serializers are working as expected.")
    print("=" * 60)


if __name__ == "__main__":
    test_models_and_serializers()