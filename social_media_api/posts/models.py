from django.conf import settings
from django.db import models


class TimeStampedModel(models.Model):
	"""Abstract base model providing created/updated timestamps."""

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		abstract = True


class Post(TimeStampedModel):
	"""Represents a user-generated post."""

	author = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name='posts',
	)
	title = models.CharField(max_length=255)
	content = models.TextField()

	class Meta:
		ordering = ('-created_at',)

	def __str__(self) -> str:
		return f"{self.title} (by {self.author})"


class Comment(TimeStampedModel):
	"""Represents a comment left on a post by a user."""

	post = models.ForeignKey(
		Post,
		on_delete=models.CASCADE,
		related_name='comments',
	)
	author = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name='comments',
	)
	content = models.TextField()

	class Meta:
		ordering = ('created_at',)

	def __str__(self) -> str:
		return f"Comment by {self.author} on {self.post}"
