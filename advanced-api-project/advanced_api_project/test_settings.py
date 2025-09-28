"""
Test-specific Django settings for advanced_api_project.

This module contains Django settings specifically configured for running tests.
It inherits from the main settings and overrides configurations to ensure:
1. Separate test database isolation
2. Faster test execution
3. Proper test environment setup

Usage:
    python manage.py test --settings=advanced_api_project.test_settings
"""

from .settings import *

# Test Database Configuration
# Override database settings for testing to ensure complete isolation
# from production/development data

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',  # Use in-memory database for fastest test execution
        'TEST': {
            'NAME': ':memory:',  # Ensure test database is always in-memory
        },
        'OPTIONS': {
            'timeout': 20,  # Database timeout for test operations
        },
    }
}

# Test-specific logging configuration
# Reduce logging noise during test execution while maintaining error visibility
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'ERROR',  # Only show errors during tests
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'api': {  # Our API app logging
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

# Disable migrations for faster test database setup
# Use this if you want to skip migrations during testing (faster but less accurate)
# Uncomment the following lines if test performance is critical:

# class DisableMigrations:
#     def __contains__(self, item):
#         return True
#     def __getitem__(self, item):
#         return None
# 
# MIGRATION_MODULES = DisableMigrations()

# Test-specific security settings
# Disable some security features for testing convenience
SECRET_KEY = 'test-secret-key-for-testing-only-not-for-production'
DEBUG = True  # Enable debug mode for better test error messages

# Disable CSRF protection for API testing
# This makes API testing easier without affecting production security
MIDDLEWARE = [middleware for middleware in MIDDLEWARE if 'csrf' not in middleware.lower()]

# Password validation - simplified for testing
# Use simpler password validation to speed up user creation in tests
AUTH_PASSWORD_VALIDATORS = []

# Email backend for testing
# Use console backend to capture emails during testing without sending real emails
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Static files - not needed for API testing
# Disable static files collection during testing for better performance
STATIC_ROOT = None
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Cache configuration for testing
# Use dummy cache backend for consistent test results
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Test-specific REST Framework settings
# Configure DRF for optimal testing
REST_FRAMEWORK.update({
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',  # Default to JSON for API tests
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
})

# Django test settings
# Configure test runner and behavior
TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# Disable debug toolbar during testing if installed
if 'debug_toolbar' in INSTALLED_APPS:
    INSTALLED_APPS = [app for app in INSTALLED_APPS if app != 'debug_toolbar']
    MIDDLEWARE = [mw for mw in MIDDLEWARE if 'debug_toolbar' not in mw]

# Test database isolation settings
# Ensure each test gets a clean database state
USE_TZ = True  # Ensure timezone handling is consistent
DATABASES['default']['ATOMIC_REQUESTS'] = True  # Wrap each test in a transaction

print("🧪 Test settings loaded - using in-memory database for isolated testing")