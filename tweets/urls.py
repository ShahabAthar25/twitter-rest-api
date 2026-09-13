from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register('', TweetViewSet, basename="tweets")

urlpatterns = [
    path("", include(router.urls)),
    path("<int:tweet_reply_pk>/replies/", ListCreateReplyView.as_view(), name="list-create-view"),
    path("replies/<int:pk>/", RetireveUpdateDestroyReplyView.as_view(), name="list-create-view")
]

