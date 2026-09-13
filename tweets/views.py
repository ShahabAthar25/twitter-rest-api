from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import ParseError
from django.shortcuts import get_object_or_404
from django.db.models import F
from django.utils import timezone
from datetime import timedelta

from .models import Tweet, Reply
from .serializers import *
from .permissions import TweetReplyPermissions, IsOwnerOrReadonly

class TweetViewSet(ModelViewSet):
    queryset = Tweet.objects.all()
    serializer_class = TweetSerializer
    permission_classes = (TweetReplyPermissions,)
    lookup_field = "pk"
    
    def list(self, request, *args, **kwargs):
        followed_tweets = Tweet.objects.filter(owner__in=request.user.following.all())
        followed_tweet_ids = followed_tweets.values_list('id', flat=True)
        additional_tweets = Tweet.objects.exclude(id__in=followed_tweet_ids)
        tweets = list(followed_tweets) + list(additional_tweets)

        queryset = self.filter_queryset(tweets)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = serializer.data
            
            return self.get_paginated_response(data)
        
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        
        return Response(data, status=status.HTTP_200_OK)
    
    def retrieve(self, request, *args, **kwargs):
        instance =  self.get_object()
        
        instance.views += 1
        instance.save()
        
        serializer = self.get_serializer(instance)
        data = serializer.data
        
        return Response(data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        tweet = self.get_object()
        
        if timezone.now() - tweet.created_at > timedelta(minutes=15):
            return Response({ "detail": "Tweets are only editable after 15 minutes of creation" }, status=status.HTTP_403_FORBIDDEN)
        
        return super().update(request, *args, **kwargs)

class ListCreateReplyView(generics.ListCreateAPIView):
    queryset = Reply.objects.all()
    serializer_class = ReplySerializer
    permission_classes = (TweetReplyPermissions,)
    lookup_field = "pk"

    def get_queryset(self):
        parent = self.request.GET.get("parent", None)
        if parent == "tweet":
            return Reply.objects.filter(tweet__id=self.kwargs.get("tweet_reply_pk"))
        elif parent == "reply":
            return Reply.objects.filter(parent_reply__id=self.kwargs.get("tweet_reply_pk"))
        else:
            raise ParseError(detail="Query parameter (parent) was either not provided or did not match the acceptable values. (ACCEPTABLE VALUES: tweet, reply)")
    
    def perform_create(self, serializer):
        parent = self.request.GET.get("parent", None)
        if not parent:
            raise ParseError(detail="Query parameter (parent) was either not provided or did not match the acceptable values. (ACCEPTABLE VALUES: tweet, reply)")
        
        if parent == "tweet":
            tweet = get_object_or_404(Tweet, pk=self.kwargs.get("tweet_reply_pk"))
            serializer.save(tweet=tweet)
        elif parent == "reply":
            reply = get_object_or_404(Reply, pk=self.kwargs.get("tweet_reply_pk"))
            serializer.save(parent_reply=reply)
        else:
            raise ParseError(detail="Query Parameter (parent) was either not provided or did not match the acceptable values. (ACCEPTABLE VALUES: tweet, reply)")

class RetireveUpdateDestroyReplyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Reply.objects.all()
    serializer_class = ReplySerializer
    permission_classes = (IsOwnerOrReadonly,)
    lookup_field = "pk"