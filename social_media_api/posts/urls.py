"""URL routing for the posts application."""

from rest_framework.routers import DefaultRouter

from .views import CommentViewSet, PostViewSet

app_name = 'posts'

router = DefaultRouter()
router.register(r'posts', PostViewSet, basename='post')
router.register(r'comments', CommentViewSet, basename='comment')

urlpatterns = router.urls
