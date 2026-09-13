from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator
from django.utils.translation import gettext as _
from django.db import models

from .managers import CustomUserManager

class User(AbstractUser):
    email = models.EmailField(_('Email Address'), unique=True)
    first_name = models.CharField(_('First Name'), max_length=150)
    last_name = models.CharField(_('Last Name'), max_length=150)
    profile_pic = models.ImageField(_('Profile Picture'), upload_to="users/", blank=True, null=True)
    website = models.URLField(_('Website'), max_length=200, validators=[MinLengthValidator(10)], blank=True, null=True)
    bio = models.CharField(_('Bio'), max_length=150, validators=[MinLengthValidator(1)], blank=True, null=True)
    followers = models.ManyToManyField('self', related_name="following_set", symmetrical=False, blank=True)
    following = models.ManyToManyField('self', related_name="followers_set", symmetrical=False, blank=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ('email', 'first_name', 'last_name')
    
    objects = CustomUserManager()

    def __str__(self):
        return f"{self.username}"

class UserFollowing(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follower_set")
    followed = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followed_set")
    followed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ["follower", "followed"]
        ordering = ["-followed_at"]
    
    def __str__(self):
        return f"{self.follower} followed {self.followed}"

# Imported here becuase tweet.models gets the custom user model which
# has not been defined yet. So, it is importd after the the custom user
# model.
from tweets.models import Tweet

class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'tweet')

    def __str__(self):
        return f"@{self.user.username}'s bookmark of tweet (ID: {self.tweet.pk})"