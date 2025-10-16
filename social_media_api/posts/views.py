"""ViewSets for posts and comments."""

from django.contrib.contenttypes.models import ContentType
from django.db.models import Prefetch
from rest_framework import filters, generics, permissions, status, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from notifications.models import Notification
from notifications.services import create_notification

from .models import Comment, Like, Post
from .permissions import IsOwnerOrReadOnly
from .serializers import CommentSerializer, LikeSerializer, PostSerializer


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
				Prefetch('comments', queryset=Comment.objects.select_related('author')),
				Prefetch('likes', queryset=Like.objects.select_related('user')),
			)
		)

	def perform_create(self, serializer):
		serializer.save(author=self.request.user)


class PostLikeView(generics.GenericAPIView):
	"""Allow authenticated users to like a post."""

	permission_classes = [permissions.IsAuthenticated]
	serializer_class = LikeSerializer

	def post(self, request, pk: int):
		post = generics.get_object_or_404(Post, pk=pk)
		like, created = Like.objects.get_or_create(user=request.user, post=post)

		if created:
			if post.author != request.user:
				Notification.objects.create(
					recipient=post.author,
					actor=request.user,
					verb='liked your post',
					content_type=ContentType.objects.get_for_model(post, for_concrete_model=False),
					object_id=post.pk,
					metadata={'post_id': post.pk, 'post_title': post.title},
				)
			status_code = status.HTTP_201_CREATED
			detail = 'Post liked.'
		else:
			status_code = status.HTTP_200_OK
			detail = 'Post already liked.'

		likes_count = Like.objects.filter(post=post).count()
		payload = {
			'detail': detail,
			'like': LikeSerializer(like, context={'request': request}).data,
			'likes_count': likes_count,
		}
		return Response(payload, status=status_code)


class PostUnlikeView(generics.GenericAPIView):
	"""Allow authenticated users to remove their like from a post."""

	permission_classes = [permissions.IsAuthenticated]

	def post(self, request, pk: int):
		post = generics.get_object_or_404(Post, pk=pk)
		deleted, _ = Like.objects.filter(user=request.user, post=post).delete()

		if deleted:
			likes_count = Like.objects.filter(post=post).count()
			return Response(
				{'detail': 'Post unliked.', 'likes_count': likes_count},
				status=status.HTTP_200_OK,
			)

		return Response(
			{'detail': 'You have not liked this post.'},
			status=status.HTTP_400_BAD_REQUEST,
		)


class FeedView(generics.ListAPIView):
	"""Return a paginated feed of posts from users the requester follows."""

	serializer_class = PostSerializer
	permission_classes = [permissions.IsAuthenticated]
	pagination_class = PostPagination

	def get_queryset(self):
		user = self.request.user
		following_users = user.following.all()
		return (
			Post.objects.filter(author__in=following_users).order_by('-created_at')
			.select_related('author')
			.prefetch_related(
				Prefetch('comments', queryset=Comment.objects.select_related('author')),
				Prefetch('likes', queryset=Like.objects.select_related('user')),
			)
		)


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
		comment = serializer.save(author=self.request.user)
		create_notification(
			recipient=comment.post.author,
			actor=self.request.user,
			verb='commented on your post',
			target=comment.post,
			metadata={'comment_id': comment.pk, 'post_id': comment.post.pk},
		)
