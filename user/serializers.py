from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model
from .models import User, Profile, Follow


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""

    password = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )

    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
            "date_joined",
        )
        read_only_fields = ("id", "date_joined")
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        """Create a new user with an encrypted password and return it."""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update a user, setting the password correctly and return it."""
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login"""

    email = serializers.CharField()
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"}
    )

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Invalid credentials")


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for Profile model"""

    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = Profile
        fields = (
            "id", "user", "username", "email", "nickname", "bio", "avatar"
        )
        read_only_fields = ("id", "user")


class FollowSerializer(serializers.ModelSerializer):
    """Serializer for Follow model"""

    follower_username = serializers.CharField(
        source="follower.username", read_only=True
    )
    following_username = serializers.CharField(
        source="following.username", read_only=True
    )

    class Meta:
        model = Follow
        fields = (
            "id",
            "follower",
            "follower_username",
            "following",
            "following_username",
            "created_at",
        )
        read_only_fields = ("id", "follower", "created_at")

    def create(self, validated_data):
        # Prevent self-following
        user = self.context["request"].user
        following = validated_data["following"]

        if user == following:
            raise serializers.ValidationError("You cannot follow yourself.")

        return Follow.objects.create(follower=user, following=following)


class UserSearchSerializer(serializers.ModelSerializer):
    """Simplified serializer for user search results"""

    profile_nickname = serializers.CharField(
        source="profile.nickname", read_only=True
    )
    profile_bio = serializers.CharField(
        source="profile.bio", read_only=True
    )

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "profile_nickname",
            "profile_bio",
        )
        read_only_fields = ("id", "username")


class AvatarImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading avatars"""

    class Meta:
        model = Profile
        fields = ("id", "avatar")
        read_only_fields = ("id",)
