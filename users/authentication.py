from django.core.cache import cache
from rest_framework_simplejwt.authentication import JWTAuthentication


class CachedJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        user_id = validated_token["user_id"]
        cache_key = f"user:{user_id}:instance"

        user = cache.get(cache_key)

        if user is None:
            # Cache miss: fetch from DB and store in cache for 15 minutes
            user = super().get_user(validated_token)
            cache.set(cache_key, user, timeout=60 * 15)

        return user
