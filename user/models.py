import os
import uuid

from django.db import models
from django.contrib.auth.models import (
    AbstractUser,
    BaseUserManager,
    UserManager as DjangoUserManager)
from django.conf import settings
from django.utils.text import slugify
from django.utils.translation import gettext as _
from rest_framework.exceptions import ValidationError


class UserManager(DjangoUserManager):
    """Define a model manager for User model with optional username."""

    use_in_migrations = True

    def _create_user(self, email, password, username=None, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError("The given email must be set")

        email = self.normalize_email(email)

        # If username is not specified, we generate it from email address.
        if not username:
            base_username = email.split("@")[0]
            username = base_username
            counter = 1
            while self.model.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1

        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, username=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, username, **extra_fields)

    def create_superuser(self, email, password, username=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if not extra_fields.get("is_staff"):
            raise ValueError("Superuser must have is_staff=True.")
        if not extra_fields.get("is_superuser"):
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, username, **extra_fields)


class User(AbstractUser):
    """
    Custom user model where email is used for authentication,
    but username still exists for compatibility.
    """
    email = models.EmailField(_("email address"), unique=True)
    username = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        db_table = "users"


def avatar_image_file_path(instance, filename):
    """Generate upload path for user profile images."""
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.nickname)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/avatars/", filename)


class Profile(models.Model):
    """User profile with additional information"""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile"
    )
    nickname = models.CharField(
        max_length=100,
        unique=True,
        help_text="A unique nickname for your account"
    )
    bio = models.TextField(
        blank=True,
        null=True,
        help_text="A short description about you"
    )
    avatar = models.ImageField(
        upload_to=avatar_image_file_path,
        help_text="A profile picture for your account",
        blank=True,
        null=True
    )

    class Meta:
        db_table = "profiles"

    def __str__(self):
        return f"{self.user.username}'s profile"


class Follow(models.Model):
    """Follow relationship between users"""

    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="following"
    )
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="followers"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.follower == self.following:
            raise ValidationError("You cannot follow yourself.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    class Meta:
        db_table = "follows"
        # unique_together = ("follower", "following")
        constraints = [
            models.UniqueConstraint(
                fields=["follower", "following"],
                name="unique_follow"
            )
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"
