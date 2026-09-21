import json

from rest_framework import generics, permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from users.serializers import (LoginSerializer, LogoutSerializer,
                               RegisterationSerializer, UserSerializer)


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
