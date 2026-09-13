from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import List

User = get_user_model()

class ListSerializer(serializers.ModelSerializer):
    followed_users = serializers.SerializerMethodField("get_followed_users_count")
    following_users = serializers.SerializerMethodField("get_following_users_count")
    
    class Meta:
        model = List
        exclude = ("owner",)
        extra_fields = {
            "created_at": { "read_only": True },
        }
    
    def create(self, validated_data):
        user = self.context["request"].user
        return List.objects.create(owner=user, **validated_data)

    def get_followed_users_count(self, obj):
        return obj.followed_users.count()

    def get_following_users_count(self, obj):
        return obj.following_users.count()
