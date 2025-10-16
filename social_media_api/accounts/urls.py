from django.urls import path
from .views import (
    UserRegistrationView,
    UserLoginView,
    UserProfileView,
    UserLogoutView
)

app_name = 'accounts'

urlpatterns = [
    # Authentication endpoints
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    
    # Profile management
    path('profile/', UserProfileView.as_view(), name='profile'),
]
