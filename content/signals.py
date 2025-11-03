from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django_celery_beat.models import PeriodicTask, CrontabSchedule
from .models import Post
from .tasks import publish_scheduled_post
import json


@receiver(post_save, sender=Post)
def schedule_post_publication(sender, instance, created, **kwargs):
    """
    Signal to schedule post-publication when a
    post with scheduled_time is created.
    """
    if instance.scheduled_time and not instance.is_published:
        # Calculate delay in seconds
        now = timezone.now()
        if instance.scheduled_time > now:
            delay = (instance.scheduled_time - now).total_seconds()
            # Schedule the task using Celery
            publish_scheduled_post.apply_async(
                args=(instance.id,),
                countdown=delay
            )
