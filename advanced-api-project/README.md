# Advanced Django API Project

A Django REST Framework project demonstrating advanced API development with custom serializers, nested relationships, and complex data structures.

## 📋 Project Overview

This project showcases the implementation of a sophisticated Django REST API that handles complex data relationships and demonstrates advanced DRF features including:

- **Custom Serializers** with nested relationship handling
- **Data Validation** with custom validation logic
- **One-to-Many Relationships** between Authors and Books
- **Comprehensive Documentation** and error handling
- **Admin Interface** for easy data management

## 🏗️ Project Structure

```
advanced-api-project/
├── advanced_api_project/          # Django project configuration
│   ├── __init__.py
│   ├── settings.py               # Project settings with DRF configuration
│   ├── urls.py                   # Main URL configuration
│   ├── wsgi.py
│   └── asgi.py
├── api/                          # Main API application
│   ├── __init__.py
│   ├── models.py                 # Author and Book models with relationships
│   ├── serializers.py            # Custom DRF serializers with validation
│   ├── admin.py                  # Django admin configuration
│   ├── views.py                  # API views (ready for implementation)
│   ├── urls.py                   # API URL patterns
│   ├── apps.py
│   ├── tests.py
│   └── migrations/               # Database migrations
├── manage.py                     # Django management script
├── test_implementation.py        # Comprehensive test script
├── db.sqlite3                    # SQLite database file
└── venv/                         # Virtual environment
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip (Python package installer)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd advanced-api-project
   ```

2. **Set up virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install django djangorestframework
   ```

4. **Apply database migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

## 📊 Data Models

### Author Model
```python
class Author(models.Model):
    name = models.CharField(max_length=100)
    
    # Supports one-to-many relationship with Books
    # Accessible via author.books.all()
```

**Features:**
- Stores author information with name validation
- One-to-many relationship with books
- Alphabetical ordering by default
- Clean string representation

### Book Model
```python
class Book(models.Model):
    title = models.CharField(max_length=200)
    publication_year = models.IntegerField()
    author = models.ForeignKey(Author, related_name='books', on_delete=models.CASCADE)
```

**Features:**
- Complete book information storage
- Foreign key relationship to Author
- Unique constraint preventing duplicate books
- Ordered by publication year (newest first)

## 🔗 Serializers

### BookSerializer
**Purpose:** Handles individual book serialization with custom validation

**Features:**
- Serializes all book fields (id, title, publication_year, author)
- **Custom Validation:** Prevents future publication years
- Comprehensive error messages
- Proper foreign key handling

**Validation Example:**
```python
# This will raise a validation error
invalid_data = {
    'title': 'Future Book',
    'publication_year': 2026,  # Future year - not allowed
    'author': 1
}
```

### AuthorSerializer
**Purpose:** Provides nested serialization of authors with their books

**Features:**
- Includes author basic information
- **Nested Books:** Automatically serializes all related books
- **Computed Fields:** 
  - `books_count`: Total number of books by author
  - `latest_publication_year`: Most recent publication year
- Read-only nested relationships for data integrity

**Example Output:**
```json
{
    "id": 1,
    "name": "J.K. Rowling",
    "books_count": 2,
    "latest_publication_year": 1998,
    "books": [
        {
            "id": 1,
            "title": "Harry Potter and the Philosopher's Stone",
            "publication_year": 1997,
            "author": 1
        },
        {
            "id": 2,
            "title": "Harry Potter and the Chamber of Secrets", 
            "publication_year": 1998,
            "author": 1
        }
    ]
}
```

### AuthorDetailSerializer
**Purpose:** Lightweight author representation for list views

**Features:**
- Efficient for performance-critical operations
- Includes book count without full book serialization
- Ideal for dropdown selections and reference fields

## 🧪 Testing

### Manual Testing with Django Shell

Test the models and serializers interactively:

```bash
python manage.py shell
```

```python
# Create test data
from api.models import Author, Book
from api.serializers import AuthorSerializer, BookSerializer

# Create author
author = Author.objects.create(name='George Orwell')

# Create book
book = Book.objects.create(
    title='1984',
    publication_year=1949,
    author=author
)

# Test serialization
author_serializer = AuthorSerializer(author)
print(author_serializer.data)
```

### Automated Testing

Run the comprehensive test script:

```bash
python test_implementation.py
```

The test script validates:
- ✅ Model creation and relationships
- ✅ Serializer functionality
- ✅ Custom validation rules
- ✅ Nested serialization
- ✅ Data integrity

## 🛡️ Validation Features

### Publication Year Validation
- **Rule:** Books cannot have future publication years
- **Implementation:** Custom `validate_publication_year` method
- **Error Message:** Clear, informative feedback

### Author Name Validation
- **Minimum Length:** At least 2 characters
- **Character Set:** Letters, spaces, hyphens, apostrophes, periods only
- **Formatting:** Automatic trimming of whitespace

### Data Integrity
- **Unique Constraints:** Prevents duplicate books by same author
- **Referential Integrity:** CASCADE deletion maintains consistency
- **Field Validation:** Comprehensive type and format checking

## 🔧 Admin Interface

Access the Django admin at `/admin/` after creating a superuser.

**Author Management:**
- List view with book counts
- Search by author name
- Alphabetical ordering

**Book Management:**
- Comprehensive list view with author and year
- Filter by publication year and author
- Search by title and author name
- Organized form fields

## 🚀 Next Steps

### Extend the API
1. **Add Views:** Implement ViewSets for CRUD operations
2. **URL Configuration:** Set up RESTful endpoints
3. **Permissions:** Add authentication and authorization
4. **Pagination:** Handle large datasets efficiently
5. **Filtering:** Add advanced filtering capabilities

### Sample ViewSet Implementation
```python
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    
    @action(detail=True, methods=['get'])
    def books(self, request, pk=None):
        author = self.get_object()
        books = author.books.all()
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)
```

## 📚 Key Learning Outcomes

This project demonstrates:

1. **Advanced Model Relationships**
   - One-to-many foreign key relationships
   - Reverse relationship access via related_name
   - CASCADE deletion behavior

2. **Custom Serializer Development**
   - Field-level validation methods
   - Object-level validation
   - Nested serialization patterns
   - Custom representation methods

3. **Data Validation Patterns**
   - Date/time validation
   - String format validation
   - Cross-field validation techniques

4. **Performance Considerations**
   - Lightweight serializers for list views
   - Efficient database queries
   - Computed fields vs database queries

5. **API Design Best Practices**
   - Clear error messages
   - Consistent data structures
   - Comprehensive documentation

## 🛠️ Technology Stack

- **Django 5.2.6:** Web framework
- **Django REST Framework 3.16.1:** API development
- **SQLite:** Database (easily replaceable)
- **Python 3.12:** Programming language

## 📝 Configuration Details

### Settings Configuration
```python
INSTALLED_APPS = [
    # ... default Django apps ...
    'rest_framework',
    'api',
]
```

### Database Configuration
- Uses Django's default SQLite database
- Easily configurable for PostgreSQL, MySQL, etc.
- Migrations handle schema changes automatically

## 🤝 Contributing

To extend this project:

1. Follow Django and DRF best practices
2. Maintain comprehensive documentation
3. Add tests for new functionality
4. Ensure proper validation and error handling

## 📄 License

This project is part of the ALX Django Learning Lab curriculum and is intended for educational purposes.

---

**Created as part of Advanced Django API Development curriculum**
*Demonstrating custom serializers, nested relationships, and complex data validation*