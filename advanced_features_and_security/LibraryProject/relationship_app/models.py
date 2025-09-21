from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver


class Author(models.Model):
	name = models.CharField(max_length=255)

	def __str__(self):
		return self.name


class Book(models.Model):
	title = models.CharField(max_length=255)
	author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')

	def __str__(self):
		return self.title

	class Meta:
		permissions = (
			("can_add_book", "Can add book"),
			("can_change_book", "Can change book"),
			("can_delete_book", "Can delete book"),
		)


class Library(models.Model):
	name = models.CharField(max_length=255)
	books = models.ManyToManyField(Book, related_name='libraries', blank=True)

	def __str__(self):
		return self.name


class Librarian(models.Model):
	name = models.CharField(max_length=255)
	library = models.OneToOneField(Library, on_delete=models.CASCADE, related_name='librarian')

	def __str__(self):
		return self.name


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

	user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='userprofile')
	role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_MEMBER)

	def __str__(self):
		return f"{self.user.username} ({self.role})"


@receiver(post_save)
def create_user_profile(sender, instance, created, **kwargs):
	"""Automatically create a UserProfile when a new User is created."""
	UserModel = get_user_model()
	if not isinstance(instance, UserModel):
		return
	if created:
		UserProfile.objects.create(user=instance)


@receiver(post_save)
def save_user_profile(sender, instance, **kwargs):
	"""Ensure the related profile is saved when the User is saved."""
	UserModel = get_user_model()
	if not isinstance(instance, UserModel):
		return
	# The profile may not exist for legacy users; create if missing.
	UserProfile.objects.get_or_create(user=instance)
