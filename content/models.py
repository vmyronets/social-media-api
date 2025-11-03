import os
import uuid

from django.db import models
from django.conf import settings
from django.utils.text import slugify


class Hashtag(models.Model):
    """Hashtag model for categorizing posts"""
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = "hashtags"

    def __str__(self):
        return f"#{self.name}"


def post_image_file_path(instance, filename):
    """Generate upload path for post images."""
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.author)}-{uuid.uuid4()}{extension}"
    return os.path.join("uploads/posts/", filename)


class Post(models.Model):
    """Post model for user posts"""

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posts"
    )
    text = models.TextField()
    scheduled_time = models.DateTimeField(blank=True, null=True)
    image = models.ImageField(
        upload_to=post_image_file_path, blank=True, null=True
    )
    hashtag = models.ManyToManyField(Hashtag, related_name="posts", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False)

    class Meta:
        db_table = "posts"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.author.username}'s post: {self.text[:50]}"


class Like(models.Model):
    """Like model for post likes"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="likes"
    )
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="likes"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "likes"
        unique_together = ("user", "post")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} likes {self.post}"


class Comment(models.Model):
    """Comment model for post comments"""

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="comments"
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "comments"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.author.username} commented on {self.post}"
