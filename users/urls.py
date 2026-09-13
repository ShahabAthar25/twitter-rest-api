from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import *

urlpatterns = [
    path('register/', RegistrationView.as_view(), name='user-register'),
    path('login/', LoginView.as_view(), name='user-login'),
    path('refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('logout/', LogoutView.as_view(), name='user-logout'),
    path('', RetrieveUpdateUserView.as_view(), name='retrieve-update-user'),
    path('<int:user_id>/followers/', ListFollowersView.as_view(), name='list-followers'),
    path('<int:user_id>/following/', ListFollowingView.as_view(), name='list-following'),
    path('<int:user_id>/follow/', FollowUnfollowView.as_view(), name='follow-unfollow-user'),
    path('bookmarks/', ListCreateBookmarksView.as_view(), name='follow-unfollow-user'),
    path('bookmarks/<int:pk>/', DestroyBookmarksView.as_view(), name='follow-unfollow-user'),
]