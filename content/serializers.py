from rest_framework import serializers
from .models import Post, Hashtag, Like, Comment
from user.serializers import UserSerializer
import re


class HashtagSerializer(serializers.ModelSerializer):
    """Serializer for Hashtag model."""

    class Meta:
        model = Hashtag
        fields = ("id", "name")
        read_only_fields = ("id",)


class PostSerializer(serializers.ModelSerializer):
    """Serializer for Post model."""

    author_username = serializers.CharField(
        source="author.username", read_only=True
    )
    hashtags = HashtagSerializer(
        source="hashtag", many=True, read_only=True
    )
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            "id",
            "author",
            "author_username",
            "text",
            "scheduled_time",
            "image",
            "hashtags",
            "created_at",
            "updated_at",
            "is_published",
            "likes_count",
            "comments_count",
        )
        read_only_fields = (
            "id", "author", "created_at", "updated_at", "is_published"
        )

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_comments_count(self, obj):
        return obj.comments.count()

    def create(self, validated_data):
        # Extract hashtags from text
        text = validated_data.get("text", "")
        hashtags = re.findall(r"#(\w+)", text)

        # If scheduled_time is provided, post is not immediately published
        if validated_data.get("scheduled_time"):
            validated_data["is_published"] = False
        else:
            validated_data["is_published"] = True

        post = Post.objects.create(**validated_data)

        # Create or get hashtags and associate with post
        for tag in hashtags:
            hashtag, created = Hashtag.objects.get_or_create(name=tag.lower())
            post.hashtag.add(hashtag)

        return post

    def update(self, instance, validated_data):
        # Update text and extract new hashtags if text changed
        if "text" in validated_data:
            text = validated_data["text"]
            hashtags = re.findall(r"#(\w+)", text)
            instance.hashtag.clear()
            for tag in hashtags:
                hashtag, created = Hashtag.objects.get_or_create(
                    name=tag.lower()
                )
                instance.hashtag.add(hashtag)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class PostImageSerializer(serializers.ModelSerializer):
    """Serializer for Post model with image."""

    class Meta:
        model = Post
        fields = ("id", "image")
        read_only_fields = ("id",)


class LikeSerializer(serializers.ModelSerializer):
    """Serializer for Like model."""

    user_username = serializers.CharField(
        source="user.username", read_only=True
    )

    class Meta:
        model = Like
        fields = ("id", "user", "user_username", "post", "created_at")
        read_only_fields = ("id", "user", "created_at")

    def validate(self, data):
        # Check if user already liked the post
        user = self.context["request"].user
        post = data["post"]
        if Like.objects.filter(user=user, post=post).exists():
            raise serializers.ValidationError(
                "You have already liked this post"
            )
        return data


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for Comment model"""

    author_username = serializers.CharField(
        source="author.username", read_only=True
    )

    class Meta:
        model = Comment
        fields = (
            "id",
            "author",
            "author_username",
            "post",
            "text",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "author", "created_at", "updated_at")
