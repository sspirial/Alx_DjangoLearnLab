"""URL routing for the posts application."""

from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import CommentViewSet, FeedView, PostLikeView, PostUnlikeView, PostViewSet

app_name = 'posts'

router = DefaultRouter()
router.register(r'posts', PostViewSet, basename='post')
router.register(r'comments', CommentViewSet, basename='comment')

urlpatterns = [
    path('feed/', FeedView.as_view(), name='feed'),
    path('posts/<int:pk>/like/', PostLikeView.as_view(), name='post-like'),
    path('posts/<int:pk>/unlike/', PostUnlikeView.as_view(), name='post-unlike'),
]

urlpatterns += router.urls
