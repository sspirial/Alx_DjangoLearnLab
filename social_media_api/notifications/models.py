"""Models powering the notifications system."""

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class NotificationQuerySet(models.QuerySet):
	"""Custom queryset helpers for notifications."""

	def unread(self):
		return self.filter(is_read=False)

	def for_user(self, user):
		return self.filter(recipient=user)


class Notification(models.Model):
	"""Represents a noteworthy action delivered to a user."""

	recipient = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name='notifications',
	)
	actor = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name='notifications_sent',
	)
	verb = models.CharField(max_length=255)
	timestamp = models.DateTimeField(auto_now_add=True)
	is_read = models.BooleanField(default=False)
	metadata = models.JSONField(blank=True, null=True)

	content_type = models.ForeignKey(
		ContentType,
		on_delete=models.CASCADE,
		related_name='notifications',
		null=True,
		blank=True,
	)
	object_id = models.PositiveIntegerField(null=True, blank=True)
	target = GenericForeignKey('content_type', 'object_id')

	objects = NotificationQuerySet.as_manager()

	class Meta:
		ordering = ('-timestamp',)
		indexes = [
			models.Index(fields=('recipient', 'is_read', 'timestamp')),
		]

	def mark_read(self) -> None:
		"""Mark the notification as read if it isn't already."""

		if not self.is_read:
			self.is_read = True
			self.save(update_fields=('is_read',))

	def __str__(self) -> str:
		target_repr = f" on {self.target}" if self.target else ''
		return f"{self.actor} {self.verb}{target_repr} for {self.recipient}"
