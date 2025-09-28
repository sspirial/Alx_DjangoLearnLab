#!/usr/bin/env python
"""
Script to create sample data for testing the advanced-api-project.

This script creates sample authors and books to test the API endpoints.
Run this script after setting up the project to populate the database
with test data.
"""

import os
import sys
import django

# Set up Django
sys.path.append('/home/munubi/Alx_DjangoLearnLab/advanced-api-project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'advanced_api_project.settings')
django.setup()

from api.models import Author, Book


def create_sample_data():
    """Create sample authors and books for testing."""
    
    print("Creating sample authors and books...")
    
    # Create authors
    authors_data = [
        "J.K. Rowling",
        "George R.R. Martin", 
        "Stephen King",
        "Agatha Christie",
        "J.R.R. Tolkien",
    ]
    
    authors = []
    for author_name in authors_data:
        author, created = Author.objects.get_or_create(name=author_name)
        authors.append(author)
        if created:
            print(f"Created author: {author.name}")
        else:
            print(f"Author already exists: {author.name}")
    
    # Create books
    books_data = [
        ("Harry Potter and the Philosopher's Stone", 1997, "J.K. Rowling"),
        ("Harry Potter and the Chamber of Secrets", 1998, "J.K. Rowling"),
        ("A Game of Thrones", 1996, "George R.R. Martin"),
        ("A Clash of Kings", 1999, "George R.R. Martin"),
        ("The Shining", 1977, "Stephen King"),
        ("It", 1986, "Stephen King"),
        ("Murder on the Orient Express", 1934, "Agatha Christie"),
        ("The ABC Murders", 1936, "Agatha Christie"),
        ("The Hobbit", 1937, "J.R.R. Tolkien"),
        ("The Lord of the Rings", 1954, "J.R.R. Tolkien"),
    ]
    
    for title, year, author_name in books_data:
        try:
            author = Author.objects.get(name=author_name)
            book, created = Book.objects.get_or_create(
                title=title,
                publication_year=year,
                author=author
            )
            if created:
                print(f"Created book: {book.title} by {book.author.name} ({book.publication_year})")
            else:
                print(f"Book already exists: {book.title}")
        except Author.DoesNotExist:
            print(f"Author not found: {author_name}")
    
    print(f"\nSample data creation complete!")
    print(f"Total authors: {Author.objects.count()}")
    print(f"Total books: {Book.objects.count()}")


if __name__ == "__main__":
    create_sample_data()