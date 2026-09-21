from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response

from users.models import User, UserFollowing
from users.serializers import UserSerializer


class ListFollowersView(generics.ListAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        user = get_object_or_404(User, pk=self.kwargs["user_id"])

        return user.followers.all()


class ListFollowingView(generics.ListAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        user = get_object_or_404(User, pk=self.kwargs["user_id"])

        return user.following.all()


class FollowUnfollowView(generics.GenericAPIView):

    def post(self, request, user_id, *args, **kwargs):
        follower = request.user
        followed = get_object_or_404(User, pk=user_id)

        if follower.pk == followed.pk:
            return Response(
                {"detail": "You cannot follow yourself."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with transaction.atomic():
                UserFollowing.objects.create(follower=follower, followed=followed)

                followed.followers_count = F("followers_count") + 1
                followed.save(update_fields=["followers_count"])

                follower.following_count = F("following_count") + 1
                follower.save(update_fields=["following_count"])

            return Response(
                f"You have followed @{followed.username}.",
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            return Response(
                "You have already followed this user.", status=status.HTTP_409_CONFLICT
            )

    def delete(self, request, user_id, *args, **kwargs):
        follower = request.user
        followed = get_object_or_404(User, pk=user_id)

        user_following = UserFollowing.objects.filter(
            follower=follower, followed=followed
        )
        if not user_following.exists():
            return Response(
                "You have not followed this user.", status=status.HTTP_409_CONFLICT
            )

        with transaction.atomic():
            # Delete the relationship row
            user_following.delete()

            # Safely decrement the counters directly in the database
            followed.followers_count = F("followers_count") - 1
            followed.save(update_fields=["followers_count"])

            follower.following_count = F("following_count") - 1
            follower.save(update_fields=["following_count"])

        return Response(
            f"You have unfollowed @{followed.username}.",
            status=status.HTTP_204_NO_CONTENT,
        )
