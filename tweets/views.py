from datetime import timedelta

from django.core.cache import cache
from django.db.models import (Case, Count, Exists, IntegerField, OuterRef,
                              Prefetch, Value, When)
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_redis import get_redis_connection
from rest_framework import generics, status
from rest_framework.exceptions import ParseError
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from users.models import User, UserFollowing

from .models import Reply, Tweet
from .permissions import IsOwnerOrReadonly, TweetReplyPermissions
from .serializers import *


class TweetViewSet(ModelViewSet):
    queryset = Tweet.objects.all()
    serializer_class = TweetSerializer
    permission_classes = (TweetReplyPermissions,)
    lookup_field = "pk"

    def _incr_view_cache(self, obj_ids, dirty_list_key):
        if not obj_ids:
            return

        conn = get_redis_connection("default")

        pipe = conn.pipeline()

        for result_id in obj_ids:
            pipe.incr(f"tweet:{result_id}:views")

        pipe.sadd(dirty_list_key, *obj_ids)

        pipe.execute()

    def list(self, request, *args, **kwargs):
        user_id = request.user.id
        page_num = request.query_params.get("page", 1)
        cache_key = f"timeline:user:{user_id}:page:{page_num}"
        dirty_tweets_key = "tweets:dirty"

        cached_data = cache.get(cache_key)
        if cached_data:
            if isinstance(cached_data, dict):
                results = cached_data.get("results", [])
            else:
                results = cached_data

            tweet_ids = [tweet["id"] for tweet in results if "id" in tweet]

            self._incr_view_cache(tweet_ids, dirty_tweets_key)

            return Response(cached_data, status=status.HTTP_200_OK)

        is_following_subquery = UserFollowing.objects.filter(
            follower=request.user, followed=OuterRef("owner")
        )

        queryset = (
            Tweet.objects.annotate(
                is_followed=Case(
                    When(Exists(is_following_subquery), then=Value(1)),
                    default=Value(0),
                    output_field=IntegerField(),
                )
            )
            .order_by("-is_followed", "-created_at")
            .prefetch_related(
                Prefetch(
                    "owner",
                    queryset=User.objects.annotate(
                        _followers_count=Count("followers", distinct=True),
                        _following_count=Count("following", distinct=True),
                    ),
                )
            )
        )
        queryset = self.filter_queryset(queryset)
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            paginated_response = self.get_paginated_response(serializer.data)

            tweet_ids = [tweet.get("id") for tweet in serializer.data]

            self._incr_view_cache(tweet_ids, dirty_tweets_key)

            # Caching for only 1 minute as this is the user feed and needs updates frequently
            cache.set(cache_key, paginated_response.data, timeout=60)
            return paginated_response

        # Non-paginated fallback
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data

        tweet_ids = [tweet.get("id") for tweet in serializer.data]

        self._incr_view_cache(tweet_ids, dirty_tweets_key)

        cache.set(cache_key, data, timeout=300)
        return Response(data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        tweet_id = kwargs.get("pk")
        cache_key = f"tweet:detail:{tweet_id}"

        data = cache.get(cache_key)
        if not data:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            data = serializer.data
            cache.set(cache_key, data, timeout=3600)

        return Response(data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        tweet = self.get_object()

        if timezone.now() - tweet.created_at > timedelta(minutes=15):
            return Response(
                {"detail": "Tweets are only editable after 15 minutes of creation"},
                status=status.HTTP_403_FORBIDDEN,
            )

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
            return Reply.objects.filter(
                parent_reply__id=self.kwargs.get("tweet_reply_pk")
            )
        else:
            raise ParseError(
                detail="Query parameter (parent) was either not provided or did not match the acceptable values. (ACCEPTABLE VALUES: tweet, reply)"
            )

    def list(self, request, *args, **kwargs):
        tweet_id = self.kwargs.get("tweet_reply_pk")
        page_num = request.query_params.get("page", 1)
        user_id = request.user.id if request.user.is_authenticated else "anonymous"

        cache_key = f"tweet:{tweet_id}:replies:user:{user_id}:page:{page_num}"
        data = cache.get(cache_key)

        if data:
            return Response(data, status.HTTP_200_OK)

        # Cache miss
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page:
            serializer = self.get_serializer(page, many=True)
            data = serializer.data

            cache.set(cache_key, data, timeout=300)  # Cache for 5 minute
            return Response(data, status=status.HTTP_200_OK)

        # Fallback
        serializer = self.get_serializer(queryset, many=True)
        cache.set(cache_key, serializer.data, timeout=300)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        parent = self.request.GET.get("parent", None)
        if not parent:
            raise ParseError(
                detail="Query parameter (parent) was either not provided or did not match the acceptable values. (ACCEPTABLE VALUES: tweet, reply)"
            )

        if parent == "tweet":
            tweet = get_object_or_404(Tweet, pk=self.kwargs.get("tweet_reply_pk"))
            serializer.save(tweet=tweet)
        elif parent == "reply":
            reply = get_object_or_404(Reply, pk=self.kwargs.get("tweet_reply_pk"))
            serializer.save(parent_reply=reply)
        else:
            raise ParseError(
                detail="Query Parameter (parent) was either not provided or did not match the acceptable values. (ACCEPTABLE VALUES: tweet, reply)"
            )


class RetireveUpdateDestroyReplyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Reply.objects.all()
    serializer_class = ReplySerializer
    permission_classes = (IsOwnerOrReadonly,)
    lookup_field = "pk"

    def retrieve(self, request, *args, **kwargs):
        reply_id = kwargs.get("pk")
        cache_key = f"reply:detail:{reply_id}"

        data = cache.get(cache_key)
        if data:
            return Response(data, status.HTTP_200_OK)

        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        cache.set(cache_key, data, timeout=600)  # Cache for 10 minutes

        return Response(data, status=status.HTTP_200_OK)
