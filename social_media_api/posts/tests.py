"""Integration tests for the posts API."""

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from notifications.models import Notification

from .models import Comment, Like, Post

User = get_user_model()


class PostApiTests(APITestCase):
	def setUp(self):
		self.user = User.objects.create_user(
			username='post_owner',
			email='post_owner@example.com',
			password='Secret123!'
		)
		self.other_user = User.objects.create_user(
			username='other_user',
			email='other_user@example.com',
			password='Secret123!'
		)

	def test_authentication_required_for_post_creation(self):
		url = reverse('posts:post-list')
		response = self.client.post(url, {'title': 'Hello', 'content': 'World'}, format='json')

		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
		self.assertEqual(Post.objects.count(), 0)

	def test_user_can_create_post(self):
		url = reverse('posts:post-list')
		self.client.force_authenticate(user=self.user)

		response = self.client.post(url, {'title': 'Hello', 'content': 'World'}, format='json')

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		post = Post.objects.get()
		self.assertEqual(post.author, self.user)
		self.assertEqual(post.title, 'Hello')

	def test_only_owner_can_update_post(self):
		post = Post.objects.create(author=self.user, title='Original', content='Body')
		url = reverse('posts:post-detail', args=[post.id])

		# Another user attempts to update
		self.client.force_authenticate(user=self.other_user)
		response = self.client.patch(url, {'title': 'Hacked'}, format='json')
		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

		# Owner updates successfully
		self.client.force_authenticate(user=self.user)
		response = self.client.patch(url, {'title': 'Updated'}, format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		post.refresh_from_db()
		self.assertEqual(post.title, 'Updated')

	def test_post_list_supports_search(self):
		Post.objects.create(author=self.user, title='Learning Django', content='Web APIs are great!')
		Post.objects.create(author=self.user, title='Gardening Tips', content='Tomatoes need sun.')

		url = reverse('posts:post-list') + '?search=django'
		response = self.client.get(url, format='json')

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['count'], 1)
		self.assertEqual(response.data['results'][0]['title'], 'Learning Django')


class CommentApiTests(APITestCase):
	def setUp(self):
		self.post_owner = User.objects.create_user(
			username='poster',
			email='poster@example.com',
			password='Secret123!'
		)
		self.commenter = User.objects.create_user(
			username='commenter',
			email='commenter@example.com',
			password='Secret123!'
		)
		self.post = Post.objects.create(author=self.post_owner, title='First Post', content='Hello world')

	def test_authentication_required_for_comment_creation(self):
		url = reverse('posts:comment-list')
		response = self.client.post(url, {'post': self.post.id, 'content': 'Nice!'}, format='json')

		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
		self.assertEqual(Comment.objects.count(), 0)

	def test_user_can_create_comment(self):
		url = reverse('posts:comment-list')
		self.client.force_authenticate(user=self.commenter)

		response = self.client.post(url, {'post': self.post.id, 'content': 'Nice!'}, format='json')

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		comment = Comment.objects.get()
		self.assertEqual(comment.author, self.commenter)
		self.assertEqual(comment.post, self.post)
		self.assertEqual(Notification.objects.count(), 1)
		notification = Notification.objects.first()
		self.assertEqual(notification.recipient, self.post_owner)
		self.assertEqual(notification.actor, self.commenter)
		self.assertEqual(notification.verb, 'commented on your post')

	def test_comment_by_author_does_not_notify_self(self):
		url = reverse('posts:comment-list')
		self.client.force_authenticate(user=self.post_owner)

		response = self.client.post(url, {'post': self.post.id, 'content': 'Thanks me!'}, format='json')

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(Notification.objects.count(), 0)

	def test_only_owner_can_delete_comment(self):
		comment = Comment.objects.create(post=self.post, author=self.commenter, content='Nice!')
		url = reverse('posts:comment-detail', args=[comment.id])

		# Another user attempts delete
		self.client.force_authenticate(user=self.post_owner)
		response = self.client.delete(url)
		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

		# Owner deletes successfully
		self.client.force_authenticate(user=self.commenter)
		response = self.client.delete(url)
		self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
		self.assertFalse(Comment.objects.filter(id=comment.id).exists())

	def test_filter_comments_by_post(self):
		other_post = Post.objects.create(author=self.post_owner, title='Second Post', content='Another one')
		Comment.objects.create(post=self.post, author=self.commenter, content='First comment')
		Comment.objects.create(post=other_post, author=self.commenter, content='Second comment')

		url = reverse('posts:comment-list') + f'?post={self.post.id}'
		response = self.client.get(url, format='json')

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['count'], 1)
		self.assertEqual(response.data['results'][0]['content'], 'First comment')


class LikeApiTests(APITestCase):
	def setUp(self):
		self.post_owner = User.objects.create_user(
			username='liker_owner',
			email='liker_owner@example.com',
			password='Secret123!'
		)
		self.other_user = User.objects.create_user(
			username='fan',
			email='fan@example.com',
			password='Secret123!'
		)
		self.post = Post.objects.create(author=self.post_owner, title='A post', content='Body')

	def _like_url(self, post_id: int) -> str:
		return reverse('posts:post-like', args=[post_id])

	def _unlike_url(self, post_id: int) -> str:
		return reverse('posts:post-unlike', args=[post_id])

	def test_authentication_required_for_like(self):
		response = self.client.post(self._like_url(self.post.id))
		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

	def test_user_can_like_post_and_notification_created(self):
		self.client.force_authenticate(user=self.other_user)
		response = self.client.post(self._like_url(self.post.id))

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertTrue(Like.objects.filter(post=self.post, user=self.other_user).exists())
		self.assertEqual(response.data['likes_count'], 1)
		self.assertEqual(Notification.objects.count(), 1)
		notification = Notification.objects.first()
		self.assertEqual(notification.recipient, self.post_owner)
		self.assertEqual(notification.actor, self.other_user)
		self.assertEqual(notification.verb, 'liked your post')

	def test_like_is_idempotent(self):
		self.client.force_authenticate(user=self.other_user)
		self.client.post(self._like_url(self.post.id))
		response = self.client.post(self._like_url(self.post.id))

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(Like.objects.filter(post=self.post, user=self.other_user).count(), 1)
		self.assertEqual(
			Notification.objects.filter(recipient=self.post_owner, verb='liked your post').count(),
			1,
		)

	def test_user_can_unlike_post(self):
		self.client.force_authenticate(user=self.other_user)
		self.client.post(self._like_url(self.post.id))

		response = self.client.post(self._unlike_url(self.post.id))

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertFalse(Like.objects.filter(post=self.post, user=self.other_user).exists())
		self.assertEqual(response.data['likes_count'], 0)

	def test_unlike_without_like_returns_error(self):
		self.client.force_authenticate(user=self.other_user)
		response = self.client.post(self._unlike_url(self.post.id))

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class FeedApiTests(APITestCase):
	def setUp(self):
		self.user = User.objects.create_user(
			username='feed_user',
			email='feed_user@example.com',
			password='Secret123!'
		)
		self.followed_user = User.objects.create_user(
			username='followed',
			email='followed@example.com',
			password='Secret123!'
		)
		self.other_user = User.objects.create_user(
			username='stranger',
			email='stranger@example.com',
			password='Secret123!'
		)
		self.feed_url = reverse('posts:feed')

	def test_feed_requires_authentication(self):
		response = self.client.get(self.feed_url)
		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

	def test_feed_returns_followed_users_posts(self):
		first_post = Post.objects.create(author=self.followed_user, title='First', content='First content')
		second_post = Post.objects.create(author=self.followed_user, title='Second', content='Second content')
		Post.objects.create(author=self.other_user, title='Hidden', content='Should not appear')

		self.user.following.add(self.followed_user)
		self.client.force_authenticate(user=self.user)

		response = self.client.get(self.feed_url)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['count'], 2)
		returned_titles = [item['title'] for item in response.data['results']]
		self.assertIn(second_post.title, returned_titles)
		self.assertIn(first_post.title, returned_titles)
		self.assertNotIn('Hidden', returned_titles)
		self.assertEqual(returned_titles[0], second_post.title)
