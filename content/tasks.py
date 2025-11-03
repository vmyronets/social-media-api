from celery import shared_task
from django.utils import timezone
from .models import Post


@shared_task
def publish_scheduled_post(post_id):
    """Celery task to publish a scheduled post."""
    try:
        post = Post.objects.get(id=post_id)
        post.is_published = True
        post.save()
        return f"Post {post_id} published successfully"
    except Post.DoesNotExist:
        return f"Post {post_id} not found"


@shared_task
def check_scheduled_posts():
    """
    Periodic task to check and publish scheduled posts.
    This task should be run periodically (e.g., every minute).
    """
    now = timezone.now()
    scheduled_posts = Post.objects.filter(
        is_published=False,
        scheduled_time__isnull=False,
        scheduled_time__lte=now
    )

    count = 0
    for post in scheduled_posts:
        post.is_published = True
        post.save()
        count += 1

    return f"Published {count} scheduled posts"
