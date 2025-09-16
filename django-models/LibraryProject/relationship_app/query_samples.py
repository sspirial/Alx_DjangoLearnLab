from django.conf import settings
from django.core.management import execute_from_command_line
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LibraryProject.settings')

import django

django.setup()

from relationship_app.models import Author, Book, Library


def books_by_author(author_name: str):
    try:
        author = Author.objects.get(name=author_name)
    except Author.DoesNotExist:
        print(f"Author '{author_name}' not found")
        return []
    qs = Book.objects.filter(author=author)
    print(f"Books by {author.name}:")
    for b in qs:
        print(f"- {b.title}")
    return list(qs)


def books_in_library(library_name: str):
    try:
        library = Library.objects.get(name=library_name)
    except Library.DoesNotExist:
        print(f"Library '{library_name}' not found")
        return []
    qs = library.books.all()
    print(f"Books in {library.name}:")
    for b in qs:
        print(f"- {b.title} by {b.author.name}")
    return list(qs)


def librarian_for_library(library_name: str):
    try:
        library = Library.objects.get(name=library_name)
    except Library.DoesNotExist:
        print(f"Library '{library_name}' not found")
        return None
    librarian = getattr(library, 'librarian', None)
    if librarian is None:
        print(f"No librarian assigned to {library.name}")
    else:
        print(f"Librarian for {library.name}: {librarian.name}")
    return librarian


if __name__ == "__main__":
    # Example seed data for quick manual testing
    if not Author.objects.exists():
        a1 = Author.objects.create(name="Jane Austen")
        a2 = Author.objects.create(name="George Orwell")
        b1 = Book.objects.create(title="Pride and Prejudice", author=a1)
        b2 = Book.objects.create(title="Emma", author=a1)
        b3 = Book.objects.create(title="1984", author=a2)
        lib = Library.objects.create(name="Central Library")
        lib.books.add(b1, b2, b3)
        # Optional: create a librarian if model is migrated
        from relationship_app.models import Librarian
        Librarian.objects.create(name="Alex Morgan", library=lib)

    books_by_author("Jane Austen")
    books_in_library("Central Library")
    librarian_for_library("Central Library")
