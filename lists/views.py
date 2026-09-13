from rest_framework import generics, status, mixins
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ModelViewSet

from .models import List
from .serializers import ListSerializer
from .permissions import IsOwnerOrAuthenticated
from tweets.models import Tweet
from tweets.serializers import TweetSerializer
from tweets.permissions import IsOwnerOrReadonly
from users.serializers import UserSerializer
from users.models import User
import json

class ListCreateListsView(generics.ListCreateAPIView):
    queryset = List.objects.all()
    serializer_class = ListSerializer

class RetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = List.objects.all()
    serializer_class = ListSerializer
    permission_classes = (IsOwnerOrReadonly,)
    lookup_field = "pk"

class FollowingListUsersView(generics.ListAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        _list = get_object_or_404(List, id=self.kwargs["pk"])
        return _list.following_users.all()

class FollowedListUsersView(ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = (IsOwnerOrAuthenticated,)
    lookup_field = "user_id"

    def get_queryset(self):
        _list = get_object_or_404(List, id=self.kwargs["pk"])
        return _list.followed_users.all()

    def create(self, request, *args, **kwargs):
        user = self.validate_user(request)
        
        _list = get_object_or_404(List, pk=kwargs.get("pk"))

        if _list.followed_users.filter(id=user.id).exists():
            return Response("You have already followed this list.", status=status.HTTP_409_CONFLICT)

        _list.followed_users.add(user)

        return Response("You have followed this list.", status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        user = kwargs.get("used_id")

        _list = get_object_or_404(List, pk=kwargs.get("pk"))

        if not _list.followed_users.filter(id=user.id).exists():
            return Response("You have not followed this list.", status=status.HTTP_400_BAD_REQUEST)

        _list.followed_users.remove(user)

        return Response("You have unfollowed this list.", status=status.HTTP_204_NO_CONTENT)

    def validate_user(self, request):
        if isinstance(request.body, bytes):
            try:
                body = json.loads(request.body)
                request.body = body
            except json.JSONDecodeError:
                return Response({"detail": "Invalid JSON"}, status=status.HTTP_400_BAD_REQUEST)

        user_id = request.body.get("user", None)
        if not user_id:
            raise ValidationError(detail="user is required.")

        user = get_object_or_404(User, pk=user_id)
        return user

class FollowUnfollowListView(generics.GenericAPIView):
    
    def post(self, request, *args, **kwargs):
        _list = get_object_or_404(List, pk=kwargs.get("pk"))

        if _list.followed_users.filter(id=request.user.id).exists():
            return Response("You have already followed this list.", status=status.HTTP_409_CONFLICT)

        _list.followed_users.add(request.user)

        return Response("You have followed this list.", status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        _list = get_object_or_404(List, pk=kwargs.get("pk"))

        if not _list.followed_users.filter(id=request.user.id).exists():
            return Response("You have not followed this list.", status=status.HTTP_400_BAD_REQUEST)

        _list.followed_users.remove(request.user)

        return Response("You have unfollowed this list.", status=status.HTTP_200_OK)

class ListTweetsView(generics.ListAPIView):
    serializer_class = TweetSerializer
    
    def get_queryset(self):
        _list = get_object_or_404(List, pk=self.kwargs["pk"])
        followed_users = _list.followed_users.all()
        
        return Tweet.objects.filter(owner__in=followed_users).order_by("-created_at")
