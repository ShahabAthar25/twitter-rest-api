from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from users.permissions import IsOwnerOrReadOnlyPermission
from users.serializers import UserSerializer


class RetrieveUpdateUserView(generics.RetrieveUpdateAPIView):

    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnlyPermission)

    def get_object(self):
        return self.request.user
