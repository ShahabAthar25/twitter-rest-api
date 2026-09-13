from rest_framework import serializers

from .models import Tweet, Reply
from users.serializers import UserSerializer

class TweetSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    
    class Meta:
        model = Tweet
        fields = "__all__"
        extra_kwargs = {
            "created_at": { "read_only": True },
            "views": { "read_only": True },
            "id": { "read_only": True },
        }

    def create(self, validated_data):
        user = self.context["request"].user
        return Tweet.objects.create(owner=user, **validated_data)

class ReplySerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)

    class Meta:
        model = Reply
        exclude = ("tweet", "parent_reply")
        extra_kwargs = {
            "created_at": { "read_only": True },
            "owner": { "read_only": True },
            "views": { "read_only": True },
            "id": { "read_only": True },
        }
    
    def create(self, validated_data):
        user = self.context["request"].user
        return Reply.objects.create(owner=user, **validated_data)