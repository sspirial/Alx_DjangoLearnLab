from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Custom User model extending AbstractUser with social features."""

    bio = models.TextField(max_length=500, blank=True, help_text="User biography")
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True,
        help_text="User profile picture",
    )
    following = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='followers',
        blank=True,
        help_text="Users this user is following",
    )

    def __str__(self):
        return self.username

    def follow(self, user: "CustomUser") -> None:
        """Add ``user`` to the current user's following list if valid."""

        if user == self:
            raise ValueError("Users cannot follow themselves.")
        self.following.add(user)

    def unfollow(self, user: "CustomUser") -> None:
        """Remove ``user`` from the current user's following list if present."""

        self.following.remove(user)

    def is_following(self, user: "CustomUser") -> bool:
        """Return True if the current user follows ``user``."""

        return self.following.filter(pk=user.pk).exists()

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
