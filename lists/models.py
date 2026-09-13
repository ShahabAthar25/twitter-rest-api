from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class List(models.Model):
    followed_users = models.ManyToManyField(User, related_name="followed_users_set", blank=True)
    following_users = models.ManyToManyField(User, related_name="following_users_set", blank=True)
    title = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title}"