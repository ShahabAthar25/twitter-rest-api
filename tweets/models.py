from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Tweet(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.CharField(max_length=280, blank=True, null=True)
    views = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    quote_tweet = models.ForeignKey('self', on_delete=models.SET_NULL, related_name="quoted_by", blank=True, null=True)

    def __str__(self):
        return f"@{self.owner.username}'s Tweet (ID: {self.pk})"

class Reply(models.Model):
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE, blank=True, null=True)
    parent_reply = models.ForeignKey('self', on_delete=models.CASCADE, related_name="replies", blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.CharField(max_length=280, blank=True, null=True)
    views = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if not self.tweet and not self.parent_reply:
            raise ValidationError('Either tweet or parent_reply must be set.')

        if self.tweet and self.parent_reply:
            raise ValidationError('Only one of tweet or parent_reply can be set.')
    
    def save(self, *args, **kwargs):
        self.clean()
        
        return super().save(*args, **kwargs)

    def __str__(self):
        if self.tweet:
            return f"@{self.owner.username}'s reply (ID: {self.pk}) to {self.tweet.owner.username}'s tweet (ID: {self.tweet.pk})"

        return f"@{self.owner.username}'s reply (ID: {self.pk}) to {self.parent_reply.owner.username}'s reply (ID: {self.parent_reply.pk})"

class Image(models.Model):
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE, blank=True, null=True)
    reply = models.ForeignKey(Reply, on_delete=models.CASCADE, blank=True, null=True)
    image = models.ImageField(upload_to="tweets/")
    description = models.CharField(max_length=280, blank=True, null=True)
    
    def clean(self):
        if not self.tweet and not self.reply:
            raise ValidationError('Either tweet or reply must be set.')

        if self.tweet and self.reply:
            raise ValidationError('Only one of tweet or reply can be set.')
    
    def save(self, *args, **kwargs):
        self.clean()
        
        return super().save(*args, **kwargs)