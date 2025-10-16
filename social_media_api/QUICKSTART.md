# Quick Start Guide - Social Media API

## Get Started in 3 Steps

### 1. Install Dependencies
```bash
pip install django djangorestframework Pillow
```

### 2. Run Migrations
```bash
cd social_media_api
python manage.py migrate
```

### 3. Start Server
```bash
python manage.py runserver
```

The API will be available at: `http://127.0.0.1:8000/`

## Quick Test with cURL

### Register a new user:
```bash
curl -X POST http://127.0.0.1:8000/api/accounts/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123",
    "password_confirm": "testpass123",
    "bio": "Test user"
  }'
```

### Login:
```bash
curl -X POST http://127.0.0.1:8000/api/accounts/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123"
  }'
```

### Get Profile (use the token from login):
```bash
curl -X GET http://127.0.0.1:8000/api/accounts/profile/ \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

## Available Endpoints

| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/api/accounts/register/` | POST | No | Register new user |
| `/api/accounts/login/` | POST | No | Login user |
| `/api/accounts/logout/` | POST | Yes | Logout user |
| `/api/accounts/profile/` | GET | Yes | Get user profile |
| `/api/accounts/profile/` | PUT/PATCH | Yes | Update profile |

## Admin Access

Create a superuser to access the admin panel:
```bash
python manage.py createsuperuser
```

Then visit: `http://127.0.0.1:8000/admin/`

For more detailed information, see the full README.md file.
