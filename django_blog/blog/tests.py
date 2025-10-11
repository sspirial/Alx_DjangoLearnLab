from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.auth import authenticate
from .forms import CustomUserCreationForm, UserProfileForm


class AuthenticationTestCase(TestCase):
    """Test cases for the authentication system"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.test_user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
    
    def test_user_registration_form(self):
        """Test user registration with custom form"""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        user = form.save()
        self.assertEqual(user.username, 'newuser')
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertEqual(user.first_name, 'New')
        self.assertEqual(user.last_name, 'User')
    
    def test_user_registration_view(self):
        """Test user registration view"""
        response = self.client.get(reverse('blog:register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create Account')
        
        # Test successful registration
        form_data = {
            'username': 'newuser2',
            'email': 'newuser2@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        response = self.client.post(reverse('blog:register'), form_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful registration
        self.assertTrue(User.objects.filter(username='newuser2').exists())
    
    def test_login_view(self):
        """Test login functionality"""
        response = self.client.get(reverse('blog:login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login')
        
        # Test successful login
        response = self.client.post(reverse('blog:login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful login
    
    def test_profile_view_requires_login(self):
        """Test that profile view requires authentication"""
        response = self.client.get(reverse('blog:profile'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_profile_view_authenticated(self):
        """Test profile view for authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('blog:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Profile')
        self.assertContains(response, 'testuser')
    
    def test_profile_update(self):
        """Test profile update functionality"""
        self.client.login(username='testuser', password='testpass123')
        
        # Test profile update
        form_data = {
            'username': 'testuser',
            'email': 'updated@example.com',
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        response = self.client.post(reverse('blog:profile'), form_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful update
        
        # Verify the update
        updated_user = User.objects.get(username='testuser')
        self.assertEqual(updated_user.email, 'updated@example.com')
        self.assertEqual(updated_user.first_name, 'Updated')
        self.assertEqual(updated_user.last_name, 'Name')
    
    def test_logout_view(self):
        """Test logout functionality"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('blog:logout'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Logged Out')
    
    def test_authentication_urls(self):
        """Test that all authentication URLs resolve correctly"""
        urls_to_test = [
            'blog:login',
            'blog:register',
            'blog:logout',
        ]
        
        for url_name in urls_to_test:
            with self.subTest(url=url_name):
                url = reverse(url_name)
                response = self.client.get(url)
                self.assertIn(response.status_code, [200, 302])  # 200 for GET, 302 for redirects
    
    def test_authenticated_urls(self):
        """Test URLs that require authentication"""
        self.client.login(username='testuser', password='testpass123')
        
        urls_to_test = [
            'blog:profile',
            'blog:change_password',
        ]
        
        for url_name in urls_to_test:
            with self.subTest(url=url_name):
                url = reverse(url_name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
    
    def test_password_change_view(self):
        """Test password change functionality"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('blog:change_password'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Change Password')


class UserProfileFormTest(TestCase):
    """Test cases for the UserProfileForm"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_profile_form_valid(self):
        """Test that profile form accepts valid data"""
        form_data = {
            'username': 'testuser',
            'email': 'updated@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
        form = UserProfileForm(data=form_data, instance=self.user)
        self.assertTrue(form.is_valid())
    
    def test_profile_form_invalid_email(self):
        """Test that profile form rejects invalid email"""
        form_data = {
            'username': 'testuser',
            'email': 'invalid-email',
            'first_name': 'Test',
            'last_name': 'User'
        }
        form = UserProfileForm(data=form_data, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
