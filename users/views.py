import json

from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import *
from .permissions import IsOwnerBookmarkPermission, IsOwnerOrReadOnlyPermission
from .serializers import *


class RegistrationView(generics.GenericAPIView):
    serializer_class = RegisterationSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        token = RefreshToken.for_user(user)

        data = serializer.data
        data["tokens"] = {"access": str(token.access_token), "refresh": str(token)}

        return Response(data, status=status.HTTP_201_CREATED)


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data

        serializer = UserSerializer(user)
        token = RefreshToken.for_user(user)

        data = serializer.data
        data["tokens"] = {"access": str(token.access_token), "refresh": str(token)}

        return Response(data, status=status.HTTP_200_OK)


class LogoutView(generics.GenericAPIView):
    serializer_class = LogoutSerializer

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            request.body = data
        except json.JSONDecodeError:
            return Response(
                {"detail": "Invalid JSON"}, status=status.HTTP_400_BAD_REQUEST
            )
        serializer = self.get_serializer(data=request.body)
        serializer.is_valid(raise_exception=True)
        refresh_token = serializer.data["refresh"]

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class RetrieveUpdateUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnlyPermission)

    def get_object(self):
        return self.request.user


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


class ListCreateBookmarksView(generics.ListCreateAPIView):
    serializer_class = BookmarkSerializer

    def get_queryset(self):
        return Bookmark.objects.filter(user__id=self.request.user.id)


class DestroyBookmarksView(generics.DestroyAPIView):
    queryset = Bookmark.objects.all()
    serializer_class = BookmarkSerializer
    permission_classes = (IsOwnerBookmarkPermission,)
    lookup_field = "pk"
