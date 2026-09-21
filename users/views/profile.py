from django.core.cache import cache
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import Response

from users.permissions import IsOwnerOrReadOnlyPermission
from users.serializers import UserSerializer


class RetrieveUpdateUserView(generics.RetrieveUpdateAPIView):

    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnlyPermission)

    def get_object(self):
        return self.request.user

    def get_cache_key(self):
        return f"user:{self.request.user.id}:profile"

    def retrieve(self, request, *args, **kwargs):
        cache_key = self.get_cache_key()

        data = cache.get(cache_key)
        # Cache miss
        if not data:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            data = serializer.data
            cache.set(cache_key, data, timeout=60 * 60 * 12)

        return Response(data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)

        if response.status_code == status.HTTP_200_OK:
            # Cache invalidated after update
            cache.delete(self.get_cache_key())

        return response
