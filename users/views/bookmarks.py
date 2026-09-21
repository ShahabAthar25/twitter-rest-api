from rest_framework import generics

from users.models import Bookmark
from users.permissions import IsOwnerBookmarkPermission
from users.serializers import BookmarkSerializer


class ListCreateBookmarksView(generics.ListCreateAPIView):
    serializer_class = BookmarkSerializer

    def get_queryset(self):
        return Bookmark.objects.filter(user__id=self.request.user.id)


class DestroyBookmarksView(generics.DestroyAPIView):
    queryset = Bookmark.objects.all()
    serializer_class = BookmarkSerializer
    permission_classes = (IsOwnerBookmarkPermission,)
    lookup_field = "pk"
