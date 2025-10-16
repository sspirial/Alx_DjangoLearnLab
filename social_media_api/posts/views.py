"""ViewSets for posts and comments."""

from django.db.models import Prefetch
from rest_framework import filters, permissions, viewsets
from rest_framework.pagination import PageNumberPagination

from .models import Comment, Post
from .permissions import IsOwnerOrReadOnly
from .serializers import CommentSerializer, PostSerializer


class PostPagination(PageNumberPagination):
	"""Default pagination for post listings."""

	page_size = 10
	page_size_query_param = 'page_size'
	max_page_size = 100


class CommentPagination(PageNumberPagination):
	"""Default pagination for comment listings."""

	page_size = 20
	page_size_query_param = 'page_size'
	max_page_size = 100


class PostViewSet(viewsets.ModelViewSet):
	"""CRUD operations for posts with search, ordering, and owner checks."""

	queryset = Post.objects.all()
	serializer_class = PostSerializer
	permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
	pagination_class = PostPagination
	filter_backends = [filters.SearchFilter, filters.OrderingFilter]
	search_fields = ('title', 'content')
	ordering_fields = ('created_at', 'updated_at', 'title')
	ordering = ('-created_at',)

	def get_queryset(self):
		"""Prefetch related data for efficient queries."""

		return (
			super()
			.get_queryset()
			.select_related('author')
			.prefetch_related(
				Prefetch('comments', queryset=Comment.objects.select_related('author'))
			)
		)

	def perform_create(self, serializer):
		serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
	"""CRUD operations for comments scoped by user and post."""

	queryset = Comment.objects.all()
	serializer_class = CommentSerializer
	permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
	pagination_class = CommentPagination
	filter_backends = [filters.SearchFilter, filters.OrderingFilter]
	search_fields = ('content',)
	ordering_fields = ('created_at', 'updated_at')
	ordering = ('created_at',)

	def get_queryset(self):
		queryset = super().get_queryset().select_related('author', 'post', 'post__author')

		post_id = self.request.query_params.get('post')
		if post_id:
			queryset = queryset.filter(post_id=post_id)

		author_id = self.request.query_params.get('author')
		if author_id:
			queryset = queryset.filter(author_id=author_id)

		return queryset

	def perform_create(self, serializer):
		serializer.save(author=self.request.user)
