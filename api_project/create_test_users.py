#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api_project.settings')
sys.path.append('/c/Users/emmun/projects/Alx_DjangoLearnLab/api_project')
django.setup()

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

# Create a test user
username = 'testuser'
password = 'testpass123'
email = 'test@example.com'

# Delete existing user if exists
User.objects.filter(username=username).delete()

# Create new user
user = User.objects.create_user(username=username, password=password, email=email)
print(f"Created user: {user.username}")

# Create token for the user
token, created = Token.objects.get_or_create(user=user)
print(f"Token for {user.username}: {token.key}")

# Create a superuser for admin access
admin_username = 'admin'
admin_password = 'admin123'
admin_email = 'admin@example.com'

# Delete existing admin if exists
User.objects.filter(username=admin_username).delete()

# Create superuser
admin_user = User.objects.create_superuser(username=admin_username, password=admin_password, email=admin_email)
print(f"Created admin user: {admin_user.username}")

# Create token for admin
admin_token, created = Token.objects.get_or_create(user=admin_user)
print(f"Token for {admin_user.username}: {admin_token.key}")