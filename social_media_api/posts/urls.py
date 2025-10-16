"""URL routing for the posts application."""

from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import CommentViewSet, FeedView, PostViewSet

app_name = 'posts'

router = DefaultRouter()
router.register(r'posts', PostViewSet, basename='post')
router.register(r'comments', CommentViewSet, basename='comment')

urlpatterns = [
    path('feed/', FeedView.as_view(), name='feed'),
]

urlpatterns += router.urls
