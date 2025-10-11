from django.urls import path
from . import views
from .views import CustomLoginView

app_name = 'blog'

urlpatterns = [
    # Blog URLs
    path('', views.home, name='home'),
    path('posts/', views.post_list, name='post_list'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    
    # Authentication URLs
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', views.custom_logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),
    path('change-password/', views.change_password_view, name='change_password'),
]