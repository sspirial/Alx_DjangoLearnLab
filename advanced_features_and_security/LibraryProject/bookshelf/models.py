from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

class Book(models.Model):
	title = models.CharField(max_length=200)
	author = models.CharField(max_length=100)
	publication_year = models.IntegerField()

	def __str__(self):
		return f"{self.title} by {self.author} ({self.publication_year})"

	class Meta:
		# Custom, human-friendly permissions used across the app
		permissions = (
			("can_view", "Can view books"),
			("can_create", "Can create books"),
			("can_edit", "Can edit books"),
			("can_delete", "Can delete books"),
		)


class CustomUserManager(BaseUserManager):
	def create_user(self, username, email=None, password=None, **extra_fields):
		if not username:
			raise ValueError("The username must be set")
		email = self.normalize_email(email)
		user = self.model(username=username, email=email, **extra_fields)
		if password:
			user.set_password(password)
		else:
			user.set_unusable_password()
		user.save(using=self._db)
		return user

	def create_superuser(self, username, email=None, password=None, **extra_fields):
		extra_fields.setdefault("is_staff", True)
		extra_fields.setdefault("is_superuser", True)
		extra_fields.setdefault("is_active", True)

		if extra_fields.get("is_staff") is not True:
			raise ValueError("Superuser must have is_staff=True.")
		if extra_fields.get("is_superuser") is not True:
			raise ValueError("Superuser must have is_superuser=True.")

		return self.create_user(username, email, password, **extra_fields)


class CustomUser(AbstractUser):
	"""Custom user with optional DOB and profile photo."""

	# Attach our manager
	objects = CustomUserManager()

	date_of_birth = models.DateField(null=True, blank=True)
	profile_photo = models.ImageField(upload_to="profile_photos/", null=True, blank=True)

	def __str__(self):
		return self.username


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


# Use CustomUser as sender to ensure signals fire for the active user model
@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
	"""Automatically create a UserProfile when a new User is created."""
	if created:
		UserProfile.objects.create(user=instance)

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
	"""Ensure the related profile is saved when the User is saved."""
	# The profile may not exist for legacy users; create if missing.
	UserProfile.objects.get_or_create(user=instance)
