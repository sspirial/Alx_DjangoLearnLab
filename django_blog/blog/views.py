from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Post

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
