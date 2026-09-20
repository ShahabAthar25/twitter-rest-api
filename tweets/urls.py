from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import *

router = DefaultRouter()
router.register("", TweetViewSet, basename="tweets")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "<int:tweet_reply_pk>/replies/", ListCreateReplyView.as_view(), name="LCV-reply"
    ),
    path(
        "replies/<int:pk>/", RetireveUpdateDestroyReplyView.as_view(), name="RUD-reply"
    ),
]
