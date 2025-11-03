from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    ProfileViewSet,
    UserSearchView,
    FollowViewSet,
)

app_name = "user"

urlpatterns = [
    # Authentication
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    # Profile
    path(
        "profile/me/", ProfileViewSet.as_view({"get": "me"}), name="profile-me"
    ),
    path(
        "profile/me/update/",
        ProfileViewSet.as_view({"put": "update_me", "patch": "update_me"}),
        name="profile-update",
    ),
    path(
        "profile/avatar-upload/",
        ProfileViewSet.as_view({"post": "avatar_upload"}),
        name="avatar-upload"
    ),
    path(
        "profiles/",
        ProfileViewSet.as_view({"get": "list"}),
        name="profile-list"
    ),
    path(
        "profiles/<int:pk>/",
        ProfileViewSet.as_view({"get": "retrieve"}),
        name="profile-detail",
    ),
    # User Search
    path("users/search/", UserSearchView.as_view(), name="user-search"),
    # Follow/Unfollow
    path("follow/", FollowViewSet.as_view({"post": "follow"}), name="follow"),
    path(
        "unfollow/",
        FollowViewSet.as_view({"post": "unfollow"}),
        name="unfollow"
    ),
    path(
        "following/",
        FollowViewSet.as_view({"get": "following"}),
        name="following-list"
    ),
    path(
        "followers/",
        FollowViewSet.as_view({"get": "followers"}),
        name="followers-list"
    ),
]
