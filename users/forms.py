from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import User, UserFollowing

class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password1', 'password2')

class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'website', 'bio')

class UserFollowingCreationForm(UserChangeForm):

    class Meta:
        model = UserFollowing
        fields = ('followed',)

class UserFollowingChangeForm(UserChangeForm):

    class Meta:
        model = UserFollowing
        fields = ('follower', 'followed')