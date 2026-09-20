from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import *

urlpatterns = [
    path("register/", RegistrationView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("refresh/", TokenRefreshView.as_view(), name="refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("", RetrieveUpdateUserView.as_view(), name="retrieve-update-user"),
    path("<int:user_id>/followers/", ListFollowersView.as_view(), name="followers"),
    path("<int:user_id>/following/", ListFollowingView.as_view(), name="following"),
    path(
        "<int:user_id>/follow/",
        FollowUnfollowView.as_view(),
        name="follow-unfollow",
    ),
    path("bookmarks/", ListCreateBookmarksView.as_view(), name="list-create-bookmarks"),
    path(
        "bookmarks/<int:pk>/",
        DestroyBookmarksView.as_view(),
        name="destroy-bookmark",
    ),
]
