from django.urls import path
from .views import PostViewSet, HashtagViewSet, LikeViewSet, CommentViewSet

app_name = "post"

urlpatterns = [
    # Posts
    path(
        "posts/",
        PostViewSet.as_view({"get": "list", "post": "create"}),
        name="post-list",
    ),
    path(
        "posts/<int:pk>/",
        PostViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="post-detail",
    ),
    path(
        "posts/my/", PostViewSet.as_view({"get": "my_posts"}), name="my-posts"
    ),
    path(
        "posts/feed/", PostViewSet.as_view({"get": "feed"}), name="post-feed"
    ),
    path(
        "posts/image-upload/",
        PostViewSet.as_view({"post": "image_upload"}),
        name="image-upload"
    ),
    # Hashtags
    path(
        "hashtags/",
        HashtagViewSet.as_view({"get": "list"}),
        name="hashtag-list"
    ),
    path(
        "hashtags/<int:pk>/",
        HashtagViewSet.as_view({"get": "retrieve"}),
        name="hashtag-detail",
    ),
    path(
        "hashtags/<int:pk>/posts/",
        HashtagViewSet.as_view({"get": "posts"}),
        name="hashtag-posts",
    ),
    # Likes
    path("likes/", LikeViewSet.as_view({"get": "list"}), name="like-list"),
    path("like/", LikeViewSet.as_view({"post": "like"}), name="like-post"),
    path(
        "unlike/", LikeViewSet.as_view({"post": "unlike"}), name="unlike-post"
    ),
    path(
        "likes/my/", LikeViewSet.as_view({"get": "my_likes"}), name="my-likes"
    ),
    # Comments
    path(
        "comments/",
        CommentViewSet.as_view({"get": "list", "post": "create"}),
        name="comment-list",
    ),
    path(
        "comments/<int:pk>/",
        CommentViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="comment-detail",
    ),
    path(
        "comments/my/",
        CommentViewSet.as_view({"get": "my_comments"}),
        name="my-comments",
    ),
]
