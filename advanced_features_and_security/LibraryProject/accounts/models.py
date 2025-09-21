from __future__ import annotations

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    """Custom manager that knows how to create users with our extra fields."""

    use_in_migrations = True

    def create_user(self, username: str, email: str | None = None, password: str | None = None, **extra_fields):
        if not username:
            raise ValueError("The Username must be set")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, username: str, email: str | None = None, password: str | None = None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(username, email, password, **extra_fields)


def user_profile_photo_path(instance: "CustomUser", filename: str) -> str:
    # Store under media/profile_photos/<username>/<filename>
    return f"profile_photos/{instance.username}/{filename}"


class CustomUser(AbstractUser):
    date_of_birth = models.DateField(blank=True, null=True, help_text=_("User's date of birth"))
    profile_photo = models.ImageField(upload_to=user_profile_photo_path, blank=True, null=True)

    objects = CustomUserManager()

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
