# API Authentication and Permissions Documentation

## Overview
This Django REST Framework API implements token-based authentication to secure endpoints and control access to resources. The authentication system ensures that only authorized users can perform CRUD operations on books.

## Authentication Configuration

### 1. Token Authentication Setup
- **Location**: `api_project/settings.py`
- **Components**:
  - `rest_framework.authtoken` added to `INSTALLED_APPS`
  - `REST_FRAMEWORK` configuration with token authentication
  - Session authentication included for browsable API

### 2. Authentication Classes
```python
'DEFAULT_AUTHENTICATION_CLASSES': [
    'rest_framework.authentication.TokenAuthentication',  # Primary authentication
    'rest_framework.authentication.SessionAuthentication',  # For browsable API
]
```

### 3. Default Permissions
```python
'DEFAULT_PERMISSION_CLASSES': [
    'rest_framework.permissions.IsAuthenticated',  # Require authentication by default
]
```

## API Endpoints

### Authentication Endpoint
- **URL**: `/api/auth/token/`
- **Method**: POST
- **Purpose**: Obtain authentication token
- **Request Body**:
  ```json
  {
    "username": "your_username",
    "password": "your_password"
  }
  ```
- **Response**:
  ```json
  {
    "token": "your_authentication_token_here"
  }
  ```

### Protected Endpoints (Require Authentication)
- **Base URL**: `/api/books_all/`
- **Methods**: GET, POST, PUT, PATCH, DELETE
- **Authentication**: Token required in header
- **Header Format**: `Authorization: Token your_token_here`

### Public Endpoints (No Authentication Required)
- **URL**: `/api/books/`
- **Method**: GET (read-only)
- **Purpose**: Public access to book list for browsing

## Permission Levels

### 1. AllowAny (Public Access)
- **Applied to**: `BookList` view (`/api/books/`)
- **Access**: Any user (authenticated or anonymous)
- **Operations**: Read-only access to book list

### 2. IsAuthenticated (Protected Access)
- **Applied to**: `BookViewSet` (`/api/books_all/`)
- **Access**: Only authenticated users with valid tokens
- **Operations**: Full CRUD operations (Create, Read, Update, Delete)

## Usage Examples

### 1. Get Authentication Token
```bash
curl -X POST http://127.0.0.1:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123"}'
```

### 2. Access Protected Endpoint
```bash
curl -H "Authorization: Token your_token_here" \
  http://127.0.0.1:8000/api/books_all/
```

### 3. Create New Book (Authenticated)
```bash
curl -X POST http://127.0.0.1:8000/api/books_all/ \
  -H "Authorization: Token your_token_here" \
  -H "Content-Type: application/json" \
  -d '{"title": "New Book", "author": "Author Name"}'
```

### 4. Access Public Endpoint (No Auth Required)
```bash
curl http://127.0.0.1:8000/api/books/
```

## Security Features

### 1. Token Management
- Tokens are automatically generated for users
- Tokens are stored securely in the database
- Tokens can be regenerated if compromised

### 2. Authentication Validation
- Invalid tokens return 401 Unauthorized
- Missing tokens return 401 Unauthorized
- Proper error messages for authentication failures

### 3. Permission Enforcement
- Different endpoints have different permission levels
- CRUD operations require authentication
- Public read access for basic book browsing

## Error Responses

### Authentication Errors
```json
{"detail": "Authentication credentials were not provided."}  // Missing token
{"detail": "Invalid token."}  // Invalid token
```

### Permission Errors
```json
{"detail": "You do not have permission to perform this action."}
```

## Test Users
For testing purposes, the following users are available:
- **Username**: `testuser`, **Password**: `testpass123`
- **Username**: `admin`, **Password**: `admin123` (superuser)

## Security Best Practices Implemented
1. Token-based authentication for API access
2. Separate public and protected endpoints
3. Proper HTTP status codes for authentication errors
4. Secure token storage in database
5. Clear permission documentation
6. Session authentication for browsable API interface