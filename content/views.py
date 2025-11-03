from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly
)
from django.db.models import Q
from django.utils import timezone

from .models import Post, Hashtag, Like, Comment
from .serializers import (
    PostSerializer,
    HashtagSerializer,
    LikeSerializer,
    CommentSerializer,
    PostImageSerializer
)
from .permissions import IsAuthorOrReadOnly


class PostViewSet(viewsets.ModelViewSet):
    """ViewSet for Post operations"""

    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["text", "hashtag__name"]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = (Post.objects.select_related("author").prefetch_related(
            "hashtag", "likes", "comments")
        )

        # Filter by published posts only for non-authors
        if self.request.user.is_authenticated:
            queryset = queryset.filter(
                Q(is_published=True) | Q(author=self.request.user)
            )
        else:
            queryset = queryset.filter(is_published=True)

        # Filter by hashtag if provided
        hashtag = self.request.query_params.get("hashtag", None)
        if hashtag:
            queryset = queryset.filter(hashtag__name__iexact=hashtag)

        return queryset

    def get_serializer_class(self):
        if self.action == "image_upload":
            return PostImageSerializer
        return PostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=False, methods=["get"])
    def my_posts(self, request):
        """Get current user's posts"""
        posts = Post.objects.filter(author=request.user).prefetch_related(
            "hashtag", "likes", "comments"
        )
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"])
    def feed(self, request):
        """Get posts from users the current user is following"""
        following_users = request.user.following.values_list(
            "following", flat=True
        )
        posts = (
            Post.objects.filter(author__in=following_users, is_published=True)
            .select_related("author")
            .prefetch_related("hashtag", "likes", "comments")
        )
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="image-upload")
    def image_upload(self, request, pk=None):
        """Upload image to post"""
        post = self.get_object()
        serializer = self.get_serializer(
            post, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class HashtagViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Hashtag operations (read-only)"""

    serializer_class = HashtagSerializer
    queryset = Hashtag.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]

    @action(detail=True, methods=["get"])
    def posts(self, request, pk=None):
        """Get all posts with this hashtag"""
        hashtag = self.get_object()
        posts = hashtag.posts.filter(
            is_published=True
        ).select_related("author")
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)


class LikeViewSet(viewsets.ModelViewSet):
    """ViewSet for Like operations"""

    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Like.objects.select_related("user", "post").all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["post"])
    def like(self, request):
        """Like a post."""
        post_id = request.data.get("post_id")
        if not post_id:
            return Response(
                {"error": "post_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            post = Post.objects.get(id=post_id, is_published=True)
        except Post.DoesNotExist:
            return Response(
                {"error": "Post not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        like, created = Like.objects.get_or_create(
            user=request.user, post=post
        )

        if created:
            serializer = self.get_serializer(like)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {"message": "Already liked this post"},
                status=status.HTTP_200_OK
            )

    @action(detail=False, methods=["post"])
    def unlike(self, request):
        """Unlike a post."""
        post_id = request.data.get("post_id")
        if not post_id:
            return Response(
                {"error": "post_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        deleted_count, _ = Like.objects.filter(
            user=request.user, post_id=post_id
        ).delete()

        if deleted_count > 0:
            return Response(
                {"message": "Successfully unliked"},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"error": "You have not liked this post"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=False, methods=["get"])
    def my_likes(self, request):
        """Get posts liked by current user."""
        likes = Like.objects.filter(
            user=request.user
        ).select_related("post__author")
        serializer = self.get_serializer(likes, many=True)
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet for Comment operations."""

    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def get_queryset(self):
        queryset = Comment.objects.select_related("author", "post").all()

        # Filter by post if provided
        post_id = self.request.query_params.get("post_id", None)
        if post_id:
            queryset = queryset.filter(post_id=post_id)

        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=False, methods=["get"])
    def my_comments(self, request):
        """Get current user's comments"""
        comments = Comment.objects.filter(
            author=request.user
        ).select_related("post")
        serializer = self.get_serializer(comments, many=True)
        return Response(serializer.data)
