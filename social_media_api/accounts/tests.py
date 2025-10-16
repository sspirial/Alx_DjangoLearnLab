from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from notifications.models import Notification

User = get_user_model()


class FollowApiTests(APITestCase):
	def setUp(self):
		self.user = User.objects.create_user(
			username='alice',
			email='alice@example.com',
			password='StrongPass123!'
		)
		self.other_user = User.objects.create_user(
			username='bob',
			email='bob@example.com',
			password='StrongPass123!'
		)

	def _follow_url(self, user_id: int) -> str:
		return reverse('accounts:follow', args=[user_id])

	def _unfollow_url(self, user_id: int) -> str:
		return reverse('accounts:unfollow', args=[user_id])

	def test_authentication_required_for_follow(self):
		response = self.client.post(self._follow_url(self.other_user.id))
		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

	def test_user_can_follow_another_user(self):
		self.client.force_authenticate(user=self.user)
		response = self.client.post(self._follow_url(self.other_user.id))

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertTrue(self.user.following.filter(pk=self.other_user.pk).exists())
		self.assertTrue(self.other_user.followers.filter(pk=self.user.pk).exists())
		self.assertEqual(Notification.objects.count(), 1)
		notification = Notification.objects.first()
		self.assertEqual(notification.recipient, self.other_user)
		self.assertEqual(notification.actor, self.user)
		self.assertEqual(notification.verb, 'started following you')

	def test_user_cannot_follow_self(self):
		self.client.force_authenticate(user=self.user)
		response = self.client.post(self._follow_url(self.user.id))

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertFalse(self.user.following.exists())
		self.assertEqual(Notification.objects.count(), 0)

	def test_follow_is_idempotent(self):
		self.client.force_authenticate(user=self.user)
		self.client.post(self._follow_url(self.other_user.id))
		response = self.client.post(self._follow_url(self.other_user.id))

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(self.user.following.count(), 1)

	def test_authentication_required_for_unfollow(self):
		response = self.client.post(self._unfollow_url(self.other_user.id))
		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

	def test_user_can_unfollow(self):
		self.client.force_authenticate(user=self.user)
		self.client.post(self._follow_url(self.other_user.id))

		response = self.client.post(self._unfollow_url(self.other_user.id))

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertFalse(self.user.following.filter(pk=self.other_user.pk).exists())

	def test_unfollow_when_not_following_returns_error(self):
		self.client.force_authenticate(user=self.user)
		response = self.client.post(self._unfollow_url(self.other_user.id))

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
