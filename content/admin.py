from django.contrib import admin
from .models import Post, Hashtag, Like, Comment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "author",
        "text_preview",
        "scheduled_time",
        "is_published",
        "created_at",
    )
    list_filter = ("is_published", "created_at", "scheduled_time")
    search_fields = ("text", "author__username")
    date_hierarchy = "created_at"
    filter_horizontal = ("hashtag",)

    def text_preview(self, obj):
        return obj.text[:50] + "..." if len(obj.text) > 50 else obj.text

    text_preview.short_description = "Text"


@admin.register(Hashtag)
class HashtagAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "post_count")
    search_fields = ("name",)

    def post_count(self, obj):
        return obj.posts.count()

    post_count.short_description = "Posts"


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "post", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "post__text")
    date_hierarchy = "created_at"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "author", "post", "text_preview", "created_at")
    list_filter = ("created_at",)
    search_fields = ("text", "author__username")
    date_hierarchy = "created_at"

    def text_preview(self, obj):
        return obj.text[:50] + "..." if len(obj.text) > 50 else obj.text

    text_preview.short_description = "Text"
