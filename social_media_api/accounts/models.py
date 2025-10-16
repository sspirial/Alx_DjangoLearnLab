from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """
    Custom User model extending AbstractUser with additional fields for social media functionality.
    """
    bio = models.TextField(max_length=500, blank=True, help_text="User biography")
    profile_picture = models.ImageField(
        upload_to='profile_pictures/', 
        blank=True, 
        null=True,
        help_text="User profile picture"
    )
    followers = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='following',
        blank=True,
        help_text="Users following this user"
    )

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
