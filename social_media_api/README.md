# Social Media API

A robust Django REST Framework-based Social Media API with user authentication, profile management, and follower functionality.

## Table of Contents
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Endpoints](#api-endpoints)
- [User Model](#user-model)
- [Authentication](#authentication)
- [Testing](#testing)
- [Project Structure](#project-structure)

## Features

- **Custom User Model**: Extended Django's AbstractUser with additional fields
  - Bio
  - Profile Picture
  - Followers/Following functionality
- **Token-based Authentication**: Secure authentication using DRF's token authentication
- **User Registration**: Create new user accounts with automatic token generation
- **User Login/Logout**: Authenticate users and manage sessions
- **Profile Management**: View and update user profiles
- **RESTful API**: Clean, well-structured API endpoints

## Tech Stack

- **Python 3.12+**
- **Django 5.2.7**
- **Django REST Framework**
- **SQLite** (default database, can be changed to PostgreSQL/MySQL)
- **Pillow** (for image handling)

## Installation

### Prerequisites
- Python 3.12 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Step-by-Step Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Alx_DjangoLearnLab/social_media_api
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   
   # On Linux/Mac:
   source venv/bin/activate
   
   # On Windows:
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install django djangorestframework Pillow
   ```

4. **Apply migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create a superuser (optional, for admin access)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

   The API will be available at `http://127.0.0.1:8000/`

## Configuration

### Settings Overview

The project is configured with the following key settings:

- **Custom User Model**: `AUTH_USER_MODEL = 'accounts.CustomUser'`
- **Authentication Classes**: Token Authentication & Session Authentication
- **Pagination**: 10 items per page
- **Media Files**: Uploaded files stored in `media/` directory

### Important Files

- `social_media_api/settings.py`: Main configuration file
- `accounts/models.py`: Custom user model definition
- `accounts/serializers.py`: API serializers
- `accounts/views.py`: API views and logic
- `accounts/urls.py`: App-level URL routing

## API Endpoints

Base URL: `http://127.0.0.1:8000/api/accounts/`

### Authentication Endpoints

#### 1. User Registration
- **URL**: `/api/accounts/register/`
- **Method**: `POST`
- **Authentication**: Not required
- **Request Body**:
  ```json
  {
    "username": "johndoe",
    "email": "john@example.com",
    "password": "securepass123",
    "password_confirm": "securepass123",
    "bio": "Software developer and tech enthusiast",
    "profile_picture": null
  }
  ```
- **Success Response** (201 Created):
  ```json
  {
    "user": {
      "id": 1,
      "username": "johndoe",
      "email": "john@example.com",
      "bio": "Software developer and tech enthusiast",
      "profile_picture": null
    },
    "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
    "message": "User registered successfully"
  }
  ```

#### 2. User Login
- **URL**: `/api/accounts/login/`
- **Method**: `POST`
- **Authentication**: Not required
- **Request Body**:
  ```json
  {
    "username": "johndoe",
    "password": "securepass123"
  }
  ```
- **Success Response** (200 OK):
  ```json
  {
    "user": {
      "id": 1,
      "username": "johndoe",
      "email": "john@example.com",
      "bio": "Software developer and tech enthusiast",
      "profile_picture": null
    },
    "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
    "message": "Login successful"
  }
  ```

#### 3. User Logout
- **URL**: `/api/accounts/logout/`
- **Method**: `POST`
- **Authentication**: Required (Token)
- **Headers**:
  ```
  Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
  ```
- **Success Response** (200 OK):
  ```json
  {
    "message": "Logout successful"
  }
  ```

#### 4. User Profile
- **URL**: `/api/accounts/profile/`
- **Methods**: `GET`, `PUT`, `PATCH`
- **Authentication**: Required (Token)
- **Headers**:
  ```
  Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
  ```

##### GET - Retrieve Profile
- **Success Response** (200 OK):
  ```json
  {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "bio": "Software developer and tech enthusiast",
    "profile_picture": null,
    "followers_count": 10,
    "following_count": 5,
    "date_joined": "2025-10-11T10:30:00Z"
  }
  ```

##### PUT/PATCH - Update Profile
- **Request Body**:
  ```json
  {
    "bio": "Updated bio text",
    "email": "newemail@example.com"
  }
  ```
- **Success Response** (200 OK):
  ```json
  {
    "id": 1,
    "username": "johndoe",
    "email": "newemail@example.com",
    "bio": "Updated bio text",
    "profile_picture": null,
    "followers_count": 10,
    "following_count": 5,
    "date_joined": "2025-10-11T10:30:00Z"
  }
  ```

## User Model

The custom user model extends Django's `AbstractUser` with the following additional fields:

| Field | Type | Description |
|-------|------|-------------|
| `bio` | TextField | User biography (max 500 characters) |
| `profile_picture` | ImageField | User's profile picture |
| `followers` | ManyToManyField | Users following this user (self-referential) |

### Relationships
- **Followers**: ManyToMany relationship with `symmetrical=False`
- **Following**: Accessible via `user.following.all()`

## Authentication

The API uses **Token Authentication** for securing endpoints.

### How to Authenticate

1. **Register or Login** to receive an authentication token
2. **Include the token** in the `Authorization` header for protected endpoints:
   ```
   Authorization: Token <your-token-here>
   ```

### Example using cURL
```bash
curl -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b" \
     http://127.0.0.1:8000/api/accounts/profile/
```

### Example using Postman
1. Select the request
2. Go to **Headers** tab
3. Add a new header:
   - Key: `Authorization`
   - Value: `Token <your-token-here>`

### Example using Python requests
```python
import requests

headers = {
    'Authorization': 'Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b'
}

response = requests.get(
    'http://127.0.0.1:8000/api/accounts/profile/',
    headers=headers
)
print(response.json())
```

## Testing

### Manual Testing with Postman

1. **Test User Registration**
   - Method: POST
   - URL: `http://127.0.0.1:8000/api/accounts/register/`
   - Body (JSON):
     ```json
     {
       "username": "testuser",
       "email": "test@example.com",
       "password": "testpass123",
       "password_confirm": "testpass123",
       "bio": "Test user bio"
     }
     ```
   - Expected: 201 Created with user data and token

2. **Test User Login**
   - Method: POST
   - URL: `http://127.0.0.1:8000/api/accounts/login/`
   - Body (JSON):
     ```json
     {
       "username": "testuser",
       "password": "testpass123"
     }
     ```
   - Expected: 200 OK with user data and token

3. **Test Profile Retrieval**
   - Method: GET
   - URL: `http://127.0.0.1:8000/api/accounts/profile/`
   - Headers: `Authorization: Token <token-from-login>`
   - Expected: 200 OK with user profile data

4. **Test Profile Update**
   - Method: PATCH
   - URL: `http://127.0.0.1:8000/api/accounts/profile/`
   - Headers: `Authorization: Token <token-from-login>`
   - Body (JSON):
     ```json
     {
       "bio": "Updated bio"
     }
     ```
   - Expected: 200 OK with updated profile

5. **Test Logout**
   - Method: POST
   - URL: `http://127.0.0.1:8000/api/accounts/logout/`
   - Headers: `Authorization: Token <token-from-login>`
   - Expected: 200 OK with logout message

### Running Unit Tests

```bash
python manage.py test accounts
```

## Project Structure

```
social_media_api/
├── accounts/                      # User authentication app
│   ├── migrations/
│   │   └── 0001_initial.py       # Initial migration for CustomUser
│   ├── __init__.py
│   ├── admin.py                  # Admin configuration
│   ├── apps.py                   # App configuration
│   ├── models.py                 # CustomUser model
│   ├── serializers.py            # DRF serializers
│   ├── urls.py                   # App URL routing
│   └── views.py                  # API views
├── social_media_api/             # Project configuration
│   ├── __init__.py
│   ├── asgi.py                   # ASGI configuration
│   ├── settings.py               # Project settings
│   ├── urls.py                   # Main URL routing
│   └── wsgi.py                   # WSGI configuration
├── media/                        # User uploaded files
│   └── profile_pictures/         # Profile pictures storage
├── db.sqlite3                    # SQLite database
├── manage.py                     # Django management script
└── README.md                     # This file
```

## Common Issues and Solutions

### Issue: Token not working
**Solution**: Ensure you're using the correct format in the Authorization header:
```
Authorization: Token <your-token>
```
NOT `Bearer <your-token>`

### Issue: Profile picture upload fails
**Solution**: Ensure Pillow is installed:
```bash
pip install Pillow
```

### Issue: CORS errors (if using frontend)
**Solution**: Install and configure django-cors-headers:
```bash
pip install django-cors-headers
```

## Next Steps

Future enhancements for this API:
- [ ] Posts/Feed functionality
- [ ] Comments and Likes
- [ ] Follow/Unfollow endpoints
- [ ] Direct messaging
- [ ] Notifications system
- [ ] Search functionality
- [ ] Pagination for feeds
- [ ] JWT authentication option
- [ ] Rate limiting
- [ ] API documentation with Swagger/ReDoc

## Admin Panel

Access the Django admin panel at `http://127.0.0.1:8000/admin/` with your superuser credentials to manage users and data.

## License

This project is part of the ALX Django Learning Lab curriculum.

## Contributors

- Your Name

## Support

For issues and questions, please open an issue in the GitHub repository.
