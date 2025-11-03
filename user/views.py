from rest_framework import viewsets, generics, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from knox.models import AuthToken
from django.contrib.auth import login
from django.db.models import Q

from .models import User, Profile, Follow
from .serializers import (
    UserSerializer,
    LoginSerializer,
    ProfileSerializer,
    FollowSerializer,
    UserSearchSerializer,
    AvatarImageSerializer
)


class RegisterView(generics.GenericAPIView):
    """API endpoint for user registration"""

    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        _, token = AuthToken.objects.create(user)
        return Response(
            {"user": UserSerializer(user).data, "token": token},
            status=status.HTTP_201_CREATED,
        )


class LoginView(generics.GenericAPIView):
    """API endpoint for user login"""

    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        login(request, user)
        _, token = AuthToken.objects.create(user)
        return Response({"user": UserSerializer(user).data, "token": token})


class LogoutView(generics.GenericAPIView):
    """API endpoint for user logout"""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        request._auth.delete()
        return Response(
            {"message": "Successfully logged out"},
            status=status.HTTP_200_OK
        )


class ProfileViewSet(viewsets.ModelViewSet):
    """Retrieve, update and delete profiles of users"""

    queryset = Profile.objects.select_related("user").all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ["user__username", "user__email", "nickname"]

    def get_permissions(self):
        """Allow anyone to view profiles, only authenticated can  modify."""
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == "avatar_upload":
            return AvatarImageSerializer
        return ProfileSerializer

    def get_queryset(self):
        return Profile.objects.select_related("user").all()

    @action(detail=False, methods=["get"])
    def me(self, request):
        """Get current user's profile (auto-created if not exists)."""
        profile, _ = Profile.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["put", "patch"])
    def update_me(self, request):
        """Create or update current user's profile."""
        profile, _ = Profile.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(
            profile, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="avatar-upload")
    def avatar_upload(self, request):
        """Upload or update user's avatar image."""
        profile, _ = Profile.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(
            profile, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserSearchView(generics.ListAPIView):
    """API endpoint for searching users"""

    serializer_class = UserSearchSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = [
        "username",
        "email",
        "first_name",
        "last_name",
        "profile__nickname",
    ]

    def get_queryset(self):
        return User.objects.select_related("profile").all()


class FollowViewSet(viewsets.ModelViewSet):
    """ViewSet for Follow/Unfollow operations"""

    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Follow.objects.select_related(
            "follower", "following"
        ).all()

    def perform_create(self, serializer):
        serializer.save(follower=self.request.user)

    @action(detail=False, methods=["post"])
    def follow(self, request):
        """Follow a user"""
        following_id = request.data.get("following_id")
        if not following_id:
            return Response(
                {"error": "following_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            following_user = User.objects.get(id=following_id)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        if request.user == following_user:
            return Response(
                {"error": "You cannot follow yourself"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        follow, created = Follow.objects.get_or_create(
            follower=request.user, following=following_user
        )

        if created:
            serializer = self.get_serializer(follow)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {"message": "Already following this user"},
                status=status.HTTP_200_OK
            )

    @action(detail=False, methods=["post"])
    def unfollow(self, request):
        """Unfollow a user"""
        following_id = request.data.get("following_id")
        if not following_id:
            return Response(
                {"error": "following_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        deleted_count, _ = Follow.objects.filter(
            follower=request.user, following_id=following_id
        ).delete()

        if deleted_count > 0:
            return Response(
                {"message": "Successfully unfollowed"},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"error": "You are not following this user"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=False, methods=["get"])
    def following(self, request):
        """Get list of users the current user is following"""
        follows = Follow.objects.filter(follower=request.user).select_related(
            "following"
        )
        serializer = self.get_serializer(follows, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def followers(self, request):
        """Get list of users following the current user"""
        follows = Follow.objects.filter(following=request.user).select_related(
            "follower"
        )
        serializer = self.get_serializer(follows, many=True)
        return Response(serializer.data)
