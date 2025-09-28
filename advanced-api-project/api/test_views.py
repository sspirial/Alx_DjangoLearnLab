"""
Comprehensive unit tests for Django REST Framework API endpoints.

This module contains thorough unit tests for all API endpoints in the advanced-api-project,
focusing on testing CRUD operations, filtering, searching, ordering, permissions, 
authentication, and response data integrity.

Test Database Isolation:
- Django automatically creates a separate test database (test_db_name) 
- Tests run in isolated transactions that are rolled back after each test
- No production or development data is affected during testing
- In-memory SQLite database used for fast test execution

Test Coverage:
- Model creation and validation
- API endpoint functionality (CRUD operations)
- Authentication and permission testing
- Data validation and error handling
- Filtering, searching, and ordering functionality
- Status code validation
- Response data integrity

The tests use Django's built-in test framework and REST Framework's test utilities
to simulate API requests and verify correct behavior under various conditions.

Test Database Configuration:
Django's test framework automatically handles database isolation by:
1. Creating a separate test database with 'test_' prefix
2. Running each test in a database transaction
3. Rolling back all changes after each test completes
4. Completely destroying the test database after the test suite finishes

This ensures complete data isolation from production/development databases.
"""

import json
from datetime import date, datetime
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from .models import Book, Author
from .serializers import BookSerializer


class ModelTestCase(TestCase):
    """
    Test cases for the Book and Author models.
    
    These tests verify that the models are correctly defined with proper
    relationships, constraints, and string representations.
    """
    
    def setUp(self):
        """Set up test data for model tests."""
        self.author = Author.objects.create(name="Test Author")
        
    def test_author_creation(self):
        """Test that Author objects are created correctly."""
        self.assertEqual(self.author.name, "Test Author")
        self.assertEqual(str(self.author), "Test Author")
        
    def test_author_ordering(self):
        """Test that authors are ordered by name."""
        author2 = Author.objects.create(name="Another Author")
        authors = Author.objects.all()
        self.assertEqual(authors[0], author2)  # "Another" comes before "Test"
        
    def test_book_creation(self):
        """Test that Book objects are created correctly."""
        book = Book.objects.create(
            title="Test Book",
            publication_year=2023,
            author=self.author
        )
        self.assertEqual(book.title, "Test Book")
        self.assertEqual(book.publication_year, 2023)
        self.assertEqual(book.author, self.author)
        self.assertEqual(str(book), "Test Book by Test Author (2023)")
        
    def test_book_ordering(self):
        """Test that books are ordered by publication year (newest first), then title."""
        book1 = Book.objects.create(
            title="Book A",
            publication_year=2022,
            author=self.author
        )
        book2 = Book.objects.create(
            title="Book B",
            publication_year=2023,
            author=self.author
        )
        book3 = Book.objects.create(
            title="Book C",
            publication_year=2023,
            author=self.author
        )
        
        books = Book.objects.all()
        self.assertEqual(books[0], book2)  # 2023, Book B
        self.assertEqual(books[1], book3)  # 2023, Book C
        self.assertEqual(books[2], book1)  # 2022, Book A
        
    def test_unique_together_constraint(self):
        """Test that the unique_together constraint prevents duplicate books."""
        Book.objects.create(
            title="Unique Book",
            publication_year=2023,
            author=self.author
        )
        
        # This should raise an IntegrityError due to unique_together constraint
        with self.assertRaises(Exception):
            Book.objects.create(
                title="Unique Book",
                publication_year=2023,
                author=self.author
            )
            
    def test_author_deletion_cascades(self):
        """Test that deleting an author deletes associated books."""
        book = Book.objects.create(
            title="Test Book",
            publication_year=2023,
            author=self.author
        )
        
        self.assertEqual(Book.objects.count(), 1)
        self.author.delete()
        self.assertEqual(Book.objects.count(), 0)  # Book should be deleted too


class BookAPITestCase(APITestCase):
    """
    Base test class for Book API endpoints.
    
    This class provides common setup and helper methods for testing
    the Book API endpoints. It creates test users, authors, and books
    for use in various test scenarios.
    """
    
    def setUp(self):
        """Set up test data for API tests."""
        # Create test users
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.admin_user = User.objects.create_superuser(
            username='admin',
            password='adminpass123',
            email='admin@example.com'
        )
        
        # Create test authors
        self.author1 = Author.objects.create(name="J.K. Rowling")
        self.author2 = Author.objects.create(name="George Orwell")
        self.author3 = Author.objects.create(name="Agatha Christie")
        
        # Create test books
        self.book1 = Book.objects.create(
            title="Harry Potter and the Philosopher's Stone",
            publication_year=1997,
            author=self.author1
        )
        self.book2 = Book.objects.create(
            title="1984",
            publication_year=1949,
            author=self.author2
        )
        self.book3 = Book.objects.create(
            title="Murder on the Orient Express",
            publication_year=1934,
            author=self.author3
        )
        
        # API client
        self.client = APIClient()
        
    def authenticate_user(self):
        """Helper method to authenticate regular user using login."""
        self.client.force_authenticate(user=self.user)
        
    def authenticate_admin(self):
        """Helper method to authenticate admin user using login."""
        self.client.force_authenticate(user=self.admin_user)
        
    def unauthenticate(self):
        """Helper method to remove authentication."""
        self.client.force_authenticate(user=None)


class BookListViewTestCase(BookAPITestCase):
    """
    Test cases for the Book List API endpoint (GET /api/books/).
    
    Tests the functionality of listing all books, including filtering,
    searching, and ordering capabilities.
    """
    
    def test_get_books_list_unauthenticated(self):
        """Test that unauthenticated users can retrieve the books list."""
        url = reverse('api:book-list-create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)
        
    def test_get_books_list_authenticated(self):
        """Test that authenticated users can retrieve the books list."""
        self.authenticate_user()
        url = reverse('api:book-list-create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)
        
    def test_books_list_ordering(self):
        """Test that books are ordered correctly by default (newest first, then by title)."""
        url = reverse('api:book-list-create')
        response = self.client.get(url)
        
        books = response.data['results']
        self.assertEqual(books[0]['title'], "Harry Potter and the Philosopher's Stone")  # 1997
        self.assertEqual(books[1]['title'], "1984")  # 1949
        self.assertEqual(books[2]['title'], "Murder on the Orient Express")  # 1934
        
    def test_books_list_custom_ordering(self):
        """Test custom ordering by title."""
        url = reverse('api:book-list-create')
        response = self.client.get(url + '?ordering=title')
        
        books = response.data['results']
        self.assertEqual(books[0]['title'], "1984")
        self.assertEqual(books[1]['title'], "Harry Potter and the Philosopher's Stone")
        self.assertEqual(books[2]['title'], "Murder on the Orient Express")
        
    def test_books_list_reverse_ordering(self):
        """Test reverse ordering by publication year."""
        url = reverse('api:book-list-create')
        response = self.client.get(url + '?ordering=publication_year')
        
        books = response.data['results']
        self.assertEqual(books[0]['publication_year'], 1934)
        self.assertEqual(books[1]['publication_year'], 1949)
        self.assertEqual(books[2]['publication_year'], 1997)
        
    def test_books_list_filtering_by_author(self):
        """Test filtering books by author name."""
        url = reverse('api:book-list-create')
        # Use author name filter instead of ID
        response = self.client.get(url + f'?author__name=J.K. Rowling')
        
        books = response.data['results']
        self.assertEqual(len(books), 1)
        self.assertEqual(books[0]['title'], "Harry Potter and the Philosopher's Stone")
        
    def test_books_list_filtering_by_publication_year(self):
        """Test filtering books by exact publication year."""
        url = reverse('api:book-list-create')
        response = self.client.get(url + '?publication_year=1949')
        
        books = response.data['results']
        self.assertEqual(len(books), 1)
        self.assertEqual(books[0]['title'], "1984")
        
    def test_books_list_filtering_by_year_range(self):
        """Test filtering books by publication year range."""
        url = reverse('api:book-list-create')
        # Create additional books to better test the range
        additional_book = Book.objects.create(
            title="Test Book 1945",
            publication_year=1945,
            author=self.author2
        )
        
        response = self.client.get(url + '?publication_year__gte=1940&publication_year__lte=1950')
        
        books = response.data['results']
        # Should include "1984" (1949) and "Test Book 1945" (1945)
        self.assertGreaterEqual(len(books), 2)
        for book in books:
            self.assertGreaterEqual(book['publication_year'], 1940)
            self.assertLessEqual(book['publication_year'], 1950)
        
    def test_books_list_search_functionality(self):
        """Test search functionality in book titles and author names."""
        url = reverse('api:book-list-create')
        
        # Search in title
        response = self.client.get(url + '?search=Potter')
        books = response.data['results']
        self.assertEqual(len(books), 1)
        self.assertEqual(books[0]['title'], "Harry Potter and the Philosopher's Stone")
        
        # Search in author name
        response = self.client.get(url + '?search=Orwell')
        books = response.data['results']
        self.assertEqual(len(books), 1)
        self.assertEqual(books[0]['title'], "1984")
        
    def test_books_list_advanced_filtering(self):
        """Test advanced filtering with title contains."""
        url = reverse('api:book-list-create')
        response = self.client.get(url + '?title__icontains=potter')
        
        books = response.data['results']
        self.assertEqual(len(books), 1)
        self.assertEqual(books[0]['title'], "Harry Potter and the Philosopher's Stone")
        
    def test_books_list_author_name_filtering(self):
        """Test filtering by author name contains."""
        url = reverse('api:book-list-create')
        response = self.client.get(url + '?author__name__icontains=rowling')
        
        books = response.data['results']
        self.assertEqual(len(books), 1)
        self.assertEqual(books[0]['title'], "Harry Potter and the Philosopher's Stone")


class BookCreateViewTestCase(BookAPITestCase):
    """
    Test cases for the Book Create API endpoint (POST /api/books/).
    
    Tests the functionality of creating new books, including validation,
    authentication requirements, and error handling.
    """
    
    def test_create_book_unauthenticated_fails(self):
        """Test that unauthenticated users cannot create books."""
        url = reverse('api:book-list-create')
        data = {
            'title': 'New Book',
            'publication_year': 2023,
            'author': self.author1.id
        }
        response = self.client.post(url, data)
        
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])
        
    def test_create_book_authenticated_success(self):
        """Test that authenticated users can create books."""
        self.authenticate_user()
        url = reverse('api:book-list-create')
        data = {
            'title': 'New Book',
            'publication_year': 2023,
            'author': self.author1.id
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New Book')
        self.assertEqual(response.data['publication_year'], 2023)
        self.assertEqual(response.data['author'], self.author1.id)
        
        # Verify book was created in database
        self.assertTrue(Book.objects.filter(title='New Book').exists())
        
    def test_create_book_future_year_fails(self):
        """Test that books with future publication years are rejected."""
        self.authenticate_user()
        url = reverse('api:book-list-create')
        future_year = date.today().year + 1
        data = {
            'title': 'Future Book',
            'publication_year': future_year,
            'author': self.author1.id
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('publication_year', response.data)
        
    def test_create_book_missing_fields_fails(self):
        """Test that creating a book with missing required fields fails."""
        self.authenticate_user()
        url = reverse('api:book-list-create')
        
        # Missing title
        data = {
            'publication_year': 2023,
            'author': self.author1.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)
        
        # Missing author
        data = {
            'title': 'New Book',
            'publication_year': 2023
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('author', response.data)
        
    def test_create_book_invalid_author_fails(self):
        """Test that creating a book with non-existent author fails."""
        self.authenticate_user()
        url = reverse('api:book-list-create')
        data = {
            'title': 'New Book',
            'publication_year': 2023,
            'author': 99999  # Non-existent author ID
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('author', response.data)
        
    def test_create_duplicate_book_fails(self):
        """Test that creating a duplicate book (same title, author, year) fails."""
        self.authenticate_user()
        url = reverse('api:book-create')
        data = {
            'title': 'Harry Potter and the Philosopher\'s Stone',
            'publication_year': 1997,
            'author': self.author1.id
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Check for either custom validation message or unique constraint error
        error_text = str(response.data).lower()
        self.assertTrue('already exists' in error_text or 'unique' in error_text)


class BookDetailViewTestCase(BookAPITestCase):
    """
    Test cases for the Book Detail API endpoint (GET /api/books/{id}/).
    
    Tests the functionality of retrieving individual book details.
    """
    
    def test_get_book_detail_unauthenticated(self):
        """Test that unauthenticated users can retrieve book details."""
        url = reverse('api:book-detail', kwargs={'pk': self.book1.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.book1.id)
        self.assertEqual(response.data['title'], self.book1.title)
        self.assertEqual(response.data['publication_year'], self.book1.publication_year)
        self.assertEqual(response.data['author'], self.book1.author.id)
        
    def test_get_book_detail_authenticated(self):
        """Test that authenticated users can retrieve book details."""
        self.authenticate_user()
        url = reverse('api:book-detail', kwargs={'pk': self.book1.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.book1.title)
        
    def test_get_nonexistent_book_fails(self):
        """Test that requesting a non-existent book returns 404."""
        url = reverse('api:book-detail', kwargs={'pk': 99999})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class BookUpdateViewTestCase(BookAPITestCase):
    """
    Test cases for the Book Update API endpoint (PUT/PATCH /api/books/{id}/).
    
    Tests the functionality of updating existing books, including validation,
    authentication requirements, and duplicate prevention.
    """
    
    def test_update_book_unauthenticated_fails(self):
        """Test that unauthenticated users cannot update books."""
        url = reverse('api:book-detail', kwargs={'pk': self.book1.id})
        data = {
            'title': 'Updated Title',
            'publication_year': 2000,
            'author': self.author1.id
        }
        response = self.client.put(url, data)
        
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])
        
    def test_update_book_authenticated_success(self):
        """Test that authenticated users can update books."""
        self.authenticate_user()
        url = reverse('api:book-detail', kwargs={'pk': self.book1.id})
        data = {
            'title': 'Updated Harry Potter',
            'publication_year': 1998,
            'author': self.author1.id
        }
        response = self.client.put(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Harry Potter')
        self.assertEqual(response.data['publication_year'], 1998)
        
        # Verify book was updated in database
        updated_book = Book.objects.get(id=self.book1.id)
        self.assertEqual(updated_book.title, 'Updated Harry Potter')
        self.assertEqual(updated_book.publication_year, 1998)
        
    def test_partial_update_book_success(self):
        """Test partial update of a book (PATCH)."""
        self.authenticate_user()
        url = reverse('api:book-detail', kwargs={'pk': self.book1.id})
        data = {
            'title': 'Partially Updated Title'
        }
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Partially Updated Title')
        # Other fields should remain unchanged
        self.assertEqual(response.data['publication_year'], self.book1.publication_year)
        self.assertEqual(response.data['author'], self.book1.author.id)
        
    def test_update_book_future_year_fails(self):
        """Test that updating a book with future publication year fails."""
        self.authenticate_user()
        url = reverse('api:book-detail', kwargs={'pk': self.book1.id})
        future_year = date.today().year + 1
        data = {
            'title': 'Updated Title',
            'publication_year': future_year,
            'author': self.author1.id
        }
        response = self.client.put(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('publication_year', response.data)
        
    def test_update_book_create_duplicate_fails(self):
        """Test that updating a book to create a duplicate fails."""
        self.authenticate_user()
        url = reverse('api:book-update', kwargs={'pk': self.book2.id})
        data = {
            'title': 'Harry Potter and the Philosopher\'s Stone',
            'publication_year': 1997,
            'author': self.author1.id
        }
        response = self.client.put(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Check for either custom validation message or unique constraint error
        error_text = str(response.data).lower()
        self.assertTrue('already exists' in error_text or 'unique' in error_text)
        
    def test_update_nonexistent_book_fails(self):
        """Test that updating a non-existent book returns 404."""
        self.authenticate_user()
        url = reverse('api:book-detail', kwargs={'pk': 99999})
        data = {
            'title': 'Updated Title',
            'publication_year': 2000,
            'author': self.author1.id
        }
        response = self.client.put(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class BookDeleteViewTestCase(BookAPITestCase):
    """
    Test cases for the Book Delete API endpoint (DELETE /api/books/{id}/).
    
    Tests the functionality of deleting books, including authentication
    requirements and proper status codes.
    """
    
    def test_delete_book_unauthenticated_fails(self):
        """Test that unauthenticated users cannot delete books."""
        url = reverse('api:book-detail', kwargs={'pk': self.book1.id})
        response = self.client.delete(url)
        
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])
        
    def test_delete_book_authenticated_success(self):
        """Test that authenticated users can delete books."""
        self.authenticate_user()
        book_id = self.book1.id
        url = reverse('api:book-detail', kwargs={'pk': book_id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify book was deleted from database
        self.assertFalse(Book.objects.filter(id=book_id).exists())
        
    def test_delete_nonexistent_book_fails(self):
        """Test that deleting a non-existent book returns 404."""
        self.authenticate_user()
        url = reverse('api:book-detail', kwargs={'pk': 99999})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class BookSerializerTestCase(TestCase):
    """
    Test cases for the BookSerializer.
    
    Tests the serialization and validation logic of the BookSerializer.
    """
    
    def setUp(self):
        """Set up test data for serializer tests."""
        self.author = Author.objects.create(name="Test Author")
        self.book = Book.objects.create(
            title="Test Book",
            publication_year=2023,
            author=self.author
        )
        
    def test_serialize_book(self):
        """Test serialization of a book instance."""
        serializer = BookSerializer(self.book)
        data = serializer.data
        
        self.assertEqual(data['title'], "Test Book")
        self.assertEqual(data['publication_year'], 2023)
        self.assertEqual(data['author'], self.author.id)
        
    def test_deserialize_valid_book(self):
        """Test deserialization of valid book data."""
        data = {
            'title': 'New Book',
            'publication_year': 2022,
            'author': self.author.id
        }
        serializer = BookSerializer(data=data)
        
        self.assertTrue(serializer.is_valid())
        book = serializer.save()
        self.assertEqual(book.title, 'New Book')
        self.assertEqual(book.publication_year, 2022)
        self.assertEqual(book.author, self.author)
        
    def test_deserialize_future_year_invalid(self):
        """Test that future publication years are invalid."""
        future_year = date.today().year + 1
        data = {
            'title': 'Future Book',
            'publication_year': future_year,
            'author': self.author.id
        }
        serializer = BookSerializer(data=data)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('publication_year', serializer.errors)
        
    def test_deserialize_missing_fields_invalid(self):
        """Test that missing required fields make serializer invalid."""
        # Missing title
        data = {
            'publication_year': 2022,
            'author': self.author.id
        }
        serializer = BookSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('title', serializer.errors)
        
        # Missing author
        data = {
            'title': 'New Book',
            'publication_year': 2022
        }
        serializer = BookSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('author', serializer.errors)


class PermissionTestCase(BookAPITestCase):
    """
    Test cases for API permissions and authentication.
    
    Tests that the proper permission levels are enforced for different
    operations and user types.
    """
    
    def test_read_operations_no_auth_required(self):
        """Test that read operations don't require authentication."""
        # List books
        url = reverse('api:book-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Get book detail
        url = reverse('api:book-detail', kwargs={'pk': self.book1.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_write_operations_require_auth(self):
        """Test that write operations require authentication."""
        data = {
            'title': 'New Book',
            'publication_year': 2023,
            'author': self.author1.id
        }
        
        # Create book
        url = reverse('api:book-list-create')
        response = self.client.post(url, data)
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])
        
        # Update book
        url = reverse('api:book-detail', kwargs={'pk': self.book1.id})
        response = self.client.put(url, data)
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])
        
        # Delete book
        response = self.client.delete(url)
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])
        
    def test_authenticated_users_can_write(self):
        """Test that authenticated users can perform write operations."""
        self.authenticate_user()
        data = {
            'title': 'New Book',
            'publication_year': 2023,
            'author': self.author1.id
        }
        
        # Create book
        url = reverse('api:book-list-create')
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Update book
        created_book_id = response.data['id']
        url = reverse('api:book-detail', kwargs={'pk': created_book_id})
        data['title'] = 'Updated Book'
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Delete book
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class IntegrationTestCase(BookAPITestCase):
    """
    Integration test cases that test complete workflows.
    
    These tests verify that the entire API works together correctly
    for real-world usage scenarios.
    """
    
    def test_complete_crud_workflow(self):
        """Test a complete CRUD workflow for a book."""
        self.authenticate_user()
        
        # Create a new author first
        author = Author.objects.create(name="Integration Test Author")
        
        # 1. Create a book
        create_url = reverse('api:book-list-create')
        create_data = {
            'title': 'Integration Test Book',
            'publication_year': 2023,
            'author': author.id
        }
        create_response = self.client.post(create_url, create_data)
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        book_id = create_response.data['id']
        
        # 2. Read the book
        detail_url = reverse('api:book-detail', kwargs={'pk': book_id})
        read_response = self.client.get(detail_url)
        self.assertEqual(read_response.status_code, status.HTTP_200_OK)
        self.assertEqual(read_response.data['title'], 'Integration Test Book')
        
        # 3. Update the book
        update_data = {
            'title': 'Updated Integration Test Book',
            'publication_year': 2024,
            'author': author.id
        }
        update_response = self.client.put(detail_url, update_data)
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.data['title'], 'Updated Integration Test Book')
        
        # 4. Delete the book
        delete_response = self.client.delete(detail_url)
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        
        # 5. Verify deletion
        final_read_response = self.client.get(detail_url)
        self.assertEqual(final_read_response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_filtering_and_search_integration(self):
        """Test integration of filtering and search functionality."""
        # Create additional test data
        python_author = Author.objects.create(name="Python Expert")
        django_book = Book.objects.create(
            title="Django for Beginners",
            publication_year=2022,
            author=python_author
        )
        flask_book = Book.objects.create(
            title="Flask Web Development",
            publication_year=2021,
            author=python_author
        )
        
        url = reverse('api:book-list-create')
        
        # Test search functionality
        response = self.client.get(url + '?search=Django')
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Django for Beginners')
        
        # Test author filtering by name
        response = self.client.get(url + f'?author__name=Python Expert')
        self.assertEqual(len(response.data['results']), 2)
        
        # Test year range filtering
        response = self.client.get(url + '?publication_year__gte=2020')
        results = response.data['results']
        # Should include Django (2022) and Flask (2021) books
        # Check that we have at least 2 books from 2020 onwards
        recent_books = [book for book in results if book['publication_year'] >= 2020]
        self.assertGreaterEqual(len(recent_books), 2)
        # Verify the specific books we expect are there
        titles = [book['title'] for book in recent_books]
        self.assertIn('Django for Beginners', titles)
        self.assertIn('Flask Web Development', titles)
            
    def test_pagination_with_many_books(self):
        """Test that pagination works correctly with many books."""
        # Create many books to test pagination
        author = Author.objects.create(name="Prolific Author")
        for i in range(25):  # Create 25 additional books
            Book.objects.create(
                title=f"Book {i+1}",
                publication_year=2020 + (i % 4),  # Years 2020-2023
                author=author
            )
            
        url = reverse('api:book-list-create')
        response = self.client.get(url)
        
        # Check that pagination is working (assuming default page size)
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('results', response.data)
        
        # Should have at least 25 + 3 (original) = 28 books total
        self.assertGreaterEqual(response.data['count'], 28)