from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from .models import Post
from .forms import CustomUserCreationForm, UserProfileForm, PasswordChangeForm

# Create your views here.

def home(request):
    """Home page showing latest 3 posts"""
    latest_posts = Post.objects.all()[:3]
    return render(request, 'blog/post_list.html', {'posts': latest_posts})

def post_list(request):
    """Display all blog posts"""
    posts = Post.objects.all()
    return render(request, 'blog/post_list.html', {'posts': posts})

def post_detail(request, post_id):
    """Display a single blog post"""
    post = get_object_or_404(Post, id=post_id)
    return render(request, 'blog/post_detail.html', {'post': post})


# Authentication Views

class CustomLoginView(LoginView):
    """Custom login view with Bootstrap styling"""
    template_name = 'registration/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('blog:home')
    
    def form_valid(self, form):
        messages.success(self.request, f'Welcome back, {form.get_user().username}!')
        return super().form_valid(form)


def custom_logout_view(request):
    """Custom logout view with confirmation message"""
    if request.user.is_authenticated:
        messages.success(request, 'You have been successfully logged out.')
        logout(request)
    return render(request, 'registration/logout.html')


def register_view(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('blog:home')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('blog:login')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})


@login_required
def profile_view(request):
    """User profile view and edit"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('blog:profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    context = {
        'form': form,
        'user': request.user
    }
    return render(request, 'registration/profile.html', context)


@login_required
def change_password_view(request):
    """Change password view"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, request.user)  # Keep user logged in
            messages.success(request, 'Your password has been changed successfully!')
            return redirect('blog:profile')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'registration/change_password.html', {'form': form})
