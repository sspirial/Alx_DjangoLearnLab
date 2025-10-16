from django.conf import settings
from django.db import models


class Post(models.Model):
	"""Represents a user-generated post."""

	author = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name='posts',
	)
	title = models.CharField(max_length=255)
	content = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ('-created_at',)

	def __str__(self) -> str:
		return f"{self.title} (by {self.author})"


class Comment(models.Model):
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
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ('created_at',)

	def __str__(self) -> str:
		return f"Comment by {self.author} on {self.post}"


class Like(models.Model):
	"""Represents a user's appreciation for a post."""

	post = models.ForeignKey(
		Post,
		on_delete=models.CASCADE,
		related_name='likes',
	)
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name='likes',
	)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ('-created_at',)
		constraints = [
			models.UniqueConstraint(fields=('post', 'user'), name='unique_post_like'),
		]

	def __str__(self) -> str:
		return f"{self.user} likes {self.post}"
