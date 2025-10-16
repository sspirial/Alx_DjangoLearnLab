# API Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Social Media API                             │
│                  Django REST Framework                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API Endpoints Layer                         │
├─────────────────────────────────────────────────────────────────┤
│  POST   /api/accounts/register/    → User Registration          │
│  POST   /api/accounts/login/       → User Login                 │
│  POST   /api/accounts/logout/      → User Logout    [Auth]      │
│  GET    /api/accounts/profile/     → Get Profile    [Auth]      │
│  PATCH  /api/accounts/profile/     → Update Profile [Auth]      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Views Layer                                │
├─────────────────────────────────────────────────────────────────┤
│  • UserRegistrationView    (CreateAPIView)                      │
│  • UserLoginView           (APIView)                             │
│  • UserLogoutView          (APIView)                             │
│  • UserProfileView         (RetrieveUpdateAPIView)              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Serializers Layer                             │
├─────────────────────────────────────────────────────────────────┤
│  • UserRegistrationSerializer  (validation + token creation)    │
│  • UserLoginSerializer         (credential validation)          │
│  • UserProfileSerializer       (profile data + counts)          │
│  • UserSerializer              (basic user data)                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Models Layer                                │
├─────────────────────────────────────────────────────────────────┤
│  CustomUser (extends AbstractUser)                              │
│    ├─ username                                                   │
│    ├─ email                                                      │
│    ├─ password                                                   │
│    ├─ bio              (custom)                                  │
│    ├─ profile_picture  (custom)                                  │
│    └─ followers        (custom ManyToMany)                       │
│                                                                  │
│  Token (from rest_framework.authtoken)                          │
│    ├─ key                                                        │
│    └─ user (ForeignKey to CustomUser)                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Database Layer                              │
│                    SQLite (Development)                          │
└─────────────────────────────────────────────────────────────────┘
```

## Authentication Flow

### Registration Flow
```
User Submission
      │
      ▼
┌──────────────────────────┐
│ POST /register/          │
│  - username              │
│  - email                 │
│  - password              │
│  - password_confirm      │
│  - bio (optional)        │
└──────────────────────────┘
      │
      ▼
┌──────────────────────────┐
│ UserRegistrationSerializer│
│  - Validate passwords    │
│  - Check email unique    │
│  - Validate data         │
└──────────────────────────┘
      │
      ▼
┌──────────────────────────┐
│ Create User              │
│  - Hash password         │
│  - Save to database      │
└──────────────────────────┘
      │
      ▼
┌──────────────────────────┐
│ Generate Token           │
│  - Create auth token     │
└──────────────────────────┘
      │
      ▼
┌──────────────────────────┐
│ Response (201 Created)   │
│  - User data             │
│  - Token                 │
│  - Success message       │
└──────────────────────────┘
```

### Login Flow
```
User Submission
      │
      ▼
┌──────────────────────────┐
│ POST /login/             │
│  - username              │
│  - password              │
└──────────────────────────┘
      │
      ▼
┌──────────────────────────┐
│ UserLoginSerializer      │
│  - Validate required     │
└──────────────────────────┘
      │
      ▼
┌──────────────────────────┐
│ Authenticate User        │
│  - Check credentials     │
└──────────────────────────┘
      │
      ├─ Invalid ──────────────┐
      │                         ▼
      │                  ┌──────────────────┐
      │                  │ 401 Unauthorized │
      │                  └──────────────────┘
      │
      ▼ Valid
┌──────────────────────────┐
│ Get/Create Token         │
└──────────────────────────┘
      │
      ▼
┌──────────────────────────┐
│ Response (200 OK)        │
│  - User data             │
│  - Token                 │
│  - Success message       │
└──────────────────────────┘
```

### Authenticated Request Flow
```
Client Request
      │
      ▼
┌──────────────────────────┐
│ Header:                  │
│ Authorization:           │
│   Token <token-key>      │
└──────────────────────────┘
      │
      ▼
┌──────────────────────────┐
│ TokenAuthentication      │
│  - Parse header          │
│  - Validate token        │
└──────────────────────────┘
      │
      ├─ Invalid ──────────────┐
      │                         ▼
      │                  ┌──────────────────┐
      │                  │ 401 Unauthorized │
      │                  └──────────────────┘
      │
      ▼ Valid
┌──────────────────────────┐
│ Attach User to Request   │
│  request.user = user     │
└──────────────────────────┘
      │
      ▼
┌──────────────────────────┐
│ Process Request          │
│  - Execute view logic    │
└──────────────────────────┘
      │
      ▼
┌──────────────────────────┐
│ Return Response          │
│  - 200 OK with data      │
└──────────────────────────┘
```

## Data Models Relationship

```
┌─────────────────────────────────────────────┐
│              CustomUser                      │
├─────────────────────────────────────────────┤
│ PK │ id                                     │
│    │ username (unique)                      │
│    │ email (unique)                         │
│    │ password (hashed)                      │
│    │ bio                                    │
│    │ profile_picture                        │
│    │ first_name                             │
│    │ last_name                              │
│    │ is_staff                               │
│    │ is_active                              │
│    │ date_joined                            │
└─────────────────────────────────────────────┘
         │                          ▲
         │ 1:1                      │ M:M
         ▼                          │
┌─────────────────────┐    ┌────────────────────┐
│      Token          │    │ followers (self)   │
├─────────────────────┤    ├────────────────────┤
│ PK │ key           │    │ from_user_id       │
│ FK │ user_id       │    │ to_user_id         │
│    │ created       │    └────────────────────┘
└─────────────────────┘
```

## Request/Response Examples

### Successful Registration
```http
POST /api/accounts/register/
Content-Type: application/json

{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "securepass123",
  "password_confirm": "securepass123",
  "bio": "Software developer"
}

→ Response (201 Created)
{
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "bio": "Software developer",
    "profile_picture": null
  },
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "message": "User registered successfully"
}
```

### Successful Login
```http
POST /api/accounts/login/
Content-Type: application/json

{
  "username": "johndoe",
  "password": "securepass123"
}

→ Response (200 OK)
{
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "bio": "Software developer",
    "profile_picture": null
  },
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "message": "Login successful"
}
```

### Get Profile (Authenticated)
```http
GET /api/accounts/profile/
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b

→ Response (200 OK)
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "bio": "Software developer",
  "profile_picture": null,
  "followers_count": 5,
  "following_count": 10,
  "date_joined": "2025-10-11T09:00:00Z"
}
```

### Unauthorized Access
```http
GET /api/accounts/profile/

→ Response (401 Unauthorized)
{
  "detail": "Authentication credentials were not provided."
}
```

## Security Features

1. **Password Hashing**
   - Passwords stored using Django's PBKDF2 algorithm
   - Never stored in plain text

2. **Token Authentication**
   - Unique token per user
   - Token required for protected endpoints
   - Token deleted on logout

3. **Email Uniqueness**
   - Enforced at serializer and database level
   - Prevents duplicate accounts

4. **Permission Classes**
   - AllowAny: Registration, Login
   - IsAuthenticated: Profile, Logout

5. **Input Validation**
   - Password confirmation check
   - Email format validation
   - Required field validation

## Error Handling

The API returns consistent error responses:

```json
{
  "detail": "Error message here"
}
```

or

```json
{
  "field_name": ["Error message for this field"]
}
```

Status codes used:
- 200: Success (GET, PUT, PATCH)
- 201: Created (POST - registration)
- 400: Bad Request (validation errors)
- 401: Unauthorized (missing/invalid token)
- 404: Not Found
- 500: Server Error
