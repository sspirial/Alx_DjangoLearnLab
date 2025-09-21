from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models

class Book(models.Model):
	title = models.CharField(max_length=200)
	author = models.CharField(max_length=100)
	publication_year = models.IntegerField()

	def __str__(self):
		return f"{self.title} by {self.author} ({self.publication_year})"


class UserProfile(models.Model):
	"""Extends Django's built-in User with a role for simple RBAC."""

	ROLE_ADMIN = 'Admin'
	ROLE_LIBRARIAN = 'Librarian'
	ROLE_MEMBER = 'Member'

	ROLE_CHOICES = (
		(ROLE_ADMIN, 'Admin'),
		(ROLE_LIBRARIAN, 'Librarian'),
		(ROLE_MEMBER, 'Member'),
	)

	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
	role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_MEMBER)

	def __str__(self):
		return f"{self.user.username} ({self.role})"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
	"""Automatically create a UserProfile when a new User is created."""
	if created:
		UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
	"""Ensure the related profile is saved when the User is saved."""
	# The profile may not exist for legacy users; create if missing.
	UserProfile.objects.get_or_create(user=instance)
