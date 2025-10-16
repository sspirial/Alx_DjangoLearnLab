from django.urls import path
from .views import (
    FollowUserView,
    UnfollowUserView,
    UserRegistrationView,
    UserLoginView,
    UserProfileView,
    UserLogoutView,
)

app_name = 'accounts'

urlpatterns = [
    # Authentication endpoints
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('follow/<int:user_id>/', FollowUserView.as_view(), name='follow'),
    path('unfollow/<int:user_id>/', UnfollowUserView.as_view(), name='unfollow'),
    
    # Profile management
    path('profile/', UserProfileView.as_view(), name='profile'),
]
