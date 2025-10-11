# Django Blog - User Authentication System

## Quick Start Guide

### Overview
This Django blog project includes a comprehensive user authentication system with registration, login, logout, and profile management features.

### Features
- ✅ User Registration with email validation
- ✅ Secure Login/Logout functionality  
- ✅ User Profile Management
- ✅ Password Change functionality
- ✅ Responsive Bootstrap UI
- ✅ CSRF Protection
- ✅ Comprehensive Testing

### URLs
- `/` - Home page
- `/login/` - User login
- `/register/` - User registration
- `/logout/` - User logout
- `/profile/` - User profile management
- `/change-password/` - Password change

### Running the Application

1. **Activate virtual environment:**
   ```bash
   source .venv/bin/activate
   ```

2. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

3. **Start the server:**
   ```bash
   python manage.py runserver
   ```

4. **Access the application:**
   Open `http://127.0.0.1:8000/` in your browser

### Testing
Run the authentication tests:
```bash
python manage.py test blog
```

### Documentation
For detailed documentation, see [AUTHENTICATION_SYSTEM_DOCS.md](AUTHENTICATION_SYSTEM_DOCS.md)

### Project Structure
```
django_blog/
├── blog/
│   ├── forms.py                 # Custom authentication forms
│   ├── views.py                 # Authentication views
│   ├── urls.py                  # URL patterns
│   ├── tests.py                 # Test suite
│   ├── templates/registration/  # Authentication templates
│   └── static/blog/css/         # Styling
├── AUTHENTICATION_SYSTEM_DOCS.md  # Detailed documentation
└── README.md                    # This file
```

### Key Components

#### Forms
- `CustomUserCreationForm` - Enhanced registration with email
- `UserProfileForm` - Profile editing
- `PasswordChangeForm` - Secure password changes

#### Views
- `register_view` - User registration
- `profile_view` - Profile management
- `CustomLoginView` - Enhanced login
- `custom_logout_view` - Logout with confirmation

#### Templates
- `login.html` - Login page
- `register.html` - Registration page
- `profile.html` - Profile management
- `logout.html` - Logout confirmation
- `change_password.html` - Password change

### Security Features
- CSRF token protection on all forms
- Password hashing with Django's built-in algorithms
- Authentication decorators for protected views
- Input validation and sanitization
- Session management

### User Experience
- Modern Bootstrap-based UI
- Responsive design for mobile devices
- Clear error messages and success notifications
- Intuitive navigation with user status indicators
- Consistent styling across all pages

---

**Next Steps:** The authentication system is ready for production use. Consider adding features like email verification, password reset, or social authentication based on your needs.