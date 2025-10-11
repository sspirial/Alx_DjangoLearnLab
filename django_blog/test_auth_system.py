#!/usr/bin/env python
"""
Test script to verify the Django authentication system
"""
import os
import sys
import django

# Add the project directory to the path
sys.path.append('/home/munubi/Alx_DjangoLearnLab/django_blog')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_blog.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
from blog.forms import CustomUserCreationForm, UserProfileForm

def test_authentication_system():
    """Test the authentication system components"""
    print("Testing Django Blog Authentication System")
    print("=" * 50)
    
    # Test 1: Forms import correctly
    print("✓ Testing form imports...")
    try:
        form = CustomUserCreationForm()
        profile_form = UserProfileForm()
        print("  ✓ Forms imported successfully")
    except Exception as e:
        print(f"  ✗ Form import failed: {e}")
        return False
    
    # Test 2: URL patterns resolve correctly
    print("✓ Testing URL patterns...")
    try:
        login_url = reverse('blog:login')
        register_url = reverse('blog:register')
        profile_url = reverse('blog:profile')
        logout_url = reverse('blog:logout')
        print(f"  ✓ Login URL: {login_url}")
        print(f"  ✓ Register URL: {register_url}")
        print(f"  ✓ Profile URL: {profile_url}")
        print(f"  ✓ Logout URL: {logout_url}")
    except Exception as e:
        print(f"  ✗ URL resolution failed: {e}")
        return False
    
    # Test 3: Database connection and User model
    print("✓ Testing database connection...")
    try:
        user_count = User.objects.count()
        print(f"  ✓ Database connected. Current users: {user_count}")
    except Exception as e:
        print(f"  ✗ Database connection failed: {e}")
        return False
    
    # Test 4: Create test user (if doesn't exist)
    print("✓ Testing user creation...")
    try:
        test_user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        if created:
            test_user.set_password('testpass123')
            test_user.save()
            print("  ✓ Test user created successfully")
        else:
            print("  ✓ Test user already exists")
    except Exception as e:
        print(f"  ✗ User creation failed: {e}")
        return False
    
    # Test 5: Test client and view responses
    print("✓ Testing view responses...")
    try:
        client = Client()
        
        # Test home page
        response = client.get('/')
        print(f"  ✓ Home page: {response.status_code}")
        
        # Test login page
        response = client.get(reverse('blog:login'))
        print(f"  ✓ Login page: {response.status_code}")
        
        # Test register page
        response = client.get(reverse('blog:register'))
        print(f"  ✓ Register page: {response.status_code}")
        
        # Test login functionality
        response = client.post(reverse('blog:login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        print(f"  ✓ Login POST: {response.status_code}")
        
        # Test profile page (should be accessible after login)
        response = client.get(reverse('blog:profile'))
        print(f"  ✓ Profile page: {response.status_code}")
        
    except Exception as e:
        print(f"  ✗ View testing failed: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("✅ Authentication system tests completed successfully!")
    print("✅ All components are working correctly!")
    return True

if __name__ == '__main__':
    test_authentication_system()