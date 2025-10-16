from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Notification

User = get_user_model()


class NotificationApiTests(APITestCase):
	def setUp(self):
		self.recipient = User.objects.create_user(
			username='recipient',
			email='recipient@example.com',
			password='Secret123!'
		)
		self.actor = User.objects.create_user(
			username='actor',
			email='actor@example.com',
			password='Secret123!'
		)
		self.notification = Notification.objects.create(
			recipient=self.recipient,
			actor=self.actor,
			verb='sent you a message',
		)

	def test_authentication_required(self):
		response = self.client.get(reverse('notifications:list'))
		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

	def test_list_notifications(self):
		self.client.force_authenticate(user=self.recipient)
		response = self.client.get(reverse('notifications:list'))

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['count'], 1)
		self.assertEqual(response.data['unread_count'], 1)
		self.assertEqual(len(response.data['results']), 1)
		self.assertFalse(response.data['results'][0]['is_read'])

	def test_mark_notification_read(self):
		self.client.force_authenticate(user=self.recipient)
		url = reverse('notifications:read', args=[self.notification.pk])

		response = self.client.post(url)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.notification.refresh_from_db()
		self.assertTrue(self.notification.is_read)
		self.assertEqual(response.data['id'], self.notification.pk)
		self.assertTrue(response.data['is_read'])

	def test_mark_notification_read_forbidden_for_other_users(self):
		self.client.force_authenticate(user=self.actor)
		url = reverse('notifications:read', args=[self.notification.pk])

		response = self.client.post(url)

		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.notification.refresh_from_db()
		self.assertFalse(self.notification.is_read)

	def test_mark_all_notifications_read(self):
		self.client.force_authenticate(user=self.recipient)
		url = reverse('notifications:read-all')

		response = self.client.post(url)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertIn('detail', response.data)
		self.notification.refresh_from_db()
		self.assertTrue(self.notification.is_read)
