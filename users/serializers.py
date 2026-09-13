from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.exceptions import NotFound, ErrorDetail

from .models import User, Bookmark
from tweets.models import Tweet

class UserSerializer(serializers.ModelSerializer):
    followers = serializers.SerializerMethodField("get_followers")
    following = serializers.SerializerMethodField("get_following")
    
    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "profile_pic", "bio", "website", "followers", "following")
    
    def get_followers(self, obj):
        return obj.followers.count()
    
    def get_following(self, obj):
        return obj.following.count()

class RegisterationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "profile_pic", "bio", "website", "password")
        extra_kwargs = {
            "password": {"write_only": True},
            "id": {"read_only": True}
        }

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Incorrect Credentials")

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True)

# Imported here because tweet serializer users UserSerializer which is defined
# above. Importing above would cause a recursion error
from tweets.serializers import TweetSerializer

class BookmarkSerializer(serializers.ModelSerializer):
    tweet = serializers.PrimaryKeyRelatedField(queryset=Tweet.objects.all())
    
    class Meta:
        model = Bookmark
        exclude = ("user",)
        extra_kwargs = {
            "id": { "read_only": True },
            "created_at": { "read_only": True },
        }

    def to_representation(self, instance):
        request = super().to_representation(instance)
        
        request["tweet"] = TweetSerializer(instance.tweet).data

        return request

    def create(self, validated_data):
        user = self.context["request"].user
        tweet = validated_data["tweet"]
        if Bookmark.objects.filter(user=user, tweet=tweet).exists():
            raise serializers.ValidationError(detail="You have already bookmarked this tweet.")
        
        return Bookmark.objects.create(user=user, **validated_data)