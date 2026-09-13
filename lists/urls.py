from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .views import *

router = DefaultRouter()
router.register('', FollowedListUsersView, basename="following-list-users")

urlpatterns = [
    path("", ListCreateListsView.as_view(), name="list-create-lists"),
    path("<int:pk>/", RetrieveUpdateDestroy.as_view(), name="retrieve-update-destroy-lists"),
    path("<int:pk>/following/", FollowingListUsersView.as_view(), name="following-users-lists"),
    path("<int:pk>/followed/", include(router.urls)),
    path("<int:pk>/follow/", FollowUnfollowListView.as_view(), name="follow-users-lists"),
    path("<int:pk>/tweets/", ListTweetsView.as_view(), name="list-tweets"),
]
