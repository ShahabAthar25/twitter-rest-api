from django.contrib.auth import get_user_model
from django.db import connection
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from tweets.models import Tweet

from .models import Bookmark, UserFollowing

User = get_user_model()


class UsersAppTests(APITestCase):

    def setUp(self):
        # Create test users
        self.user1 = User.objects.create_user(
            username="testuser1",
            email="user1@example.com",
            password="Password123!",
            first_name="John",
            last_name="Doe",
        )
        self.user2 = User.objects.create_user(
            username="testuser2",
            email="user2@example.com",
            password="Password123!",
            first_name="Jane",
            last_name="Smith",
        )

        self.tweet = Tweet.objects.create(content="Hello World!", owner=self.user2)

        # Generate tokens for authenticated endpoints
        self.token1 = RefreshToken.for_user(self.user1)
        self.token2 = RefreshToken.for_user(self.user2)

    def authenticate_user1(self):
        """Helper method to authenticate user1 on the client."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token1.access_token}")

    # ==========================================
    # AUTHENTICATION TESTS
    # ==========================================

    def test_registration_success(self):
        url = reverse("register")

        data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "Password123!",
            "first_name": "New",
            "last_name": "User",
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("tokens", response.data)
        self.assertIn("access", response.data["tokens"])

    def test_login_success(self):
        url = reverse("login")

        data = {"username": "testuser1", "password": "Password123!"}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("tokens", response.data)

    def test_logout_success(self):
        url = reverse("logout")

        self.authenticate_user1()

        data = {"refresh": str(self.token1)}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)

    # ==========================================
    # USER PROFILE TESTS
    # ==========================================

    def test_retrieve_profile(self):
        url = reverse("retrieve-update-user")
        self.authenticate_user1()
        # Cache miss. 1 auth query (Data comes from auth query i.e. IsAuthenticated)
        with self.assertNumQueries(1):
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["username"], self.user1.username)

        # Cahce hitL 1 auth query (Data comes from cache)
        with self.assertNumQueries(1):
            response = self.client.get(url)

    def test_update_profile(self):
        url = reverse("retrieve-update-user")
        self.authenticate_user1()
        data = {
            "username": "testuser1",
            "email": "user1@example.com",
            "first_name": "UpdatedName",
            "last_name": "Doe",
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.first_name, "UpdatedName")

    # ==========================================
    # RELATIONSHIP (FOLLOW/UNFOLLOW) TESTS
    # ==========================================

    def test_follow_user_and_counters(self):
        url = reverse("follow-unfollow", kwargs={"user_id": self.user2.pk})
        self.authenticate_user1()

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Assert relationship row exists
        self.assertTrue(
            UserFollowing.objects.filter(
                follower=self.user1, followed=self.user2
            ).exists()
        )

        # Assert atomic database counters incremented correctly
        self.user1.refresh_from_db()
        self.user2.refresh_from_db()
        self.assertEqual(self.user1.following_count, 1)
        self.assertEqual(self.user2.followers_count, 1)

    def test_follow_self_fails(self):
        url = reverse("follow-unfollow", kwargs={"user_id": self.user1.pk})
        self.authenticate_user1()

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unfollow_user_and_counters(self):
        # Pre-create follow relationship
        UserFollowing.objects.create(follower=self.user1, followed=self.user2)
        User.objects.filter(pk=self.user1.pk).update(following_count=1)
        User.objects.filter(pk=self.user2.pk).update(followers_count=1)

        url = reverse("follow-unfollow", kwargs={"user_id": self.user2.pk})
        self.authenticate_user1()

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Assert relationship row deleted
        self.assertFalse(
            UserFollowing.objects.filter(
                follower=self.user1, followed=self.user2
            ).exists()
        )

        # Assert atomic database counters decremented correctly
        self.user1.refresh_from_db()
        self.user2.refresh_from_db()
        self.assertEqual(self.user1.following_count, 0)
        self.assertEqual(self.user2.followers_count, 0)

    def test_list_followers_and_following(self):
        self.authenticate_user1()

        UserFollowing.objects.create(follower=self.user1, followed=self.user2)

        # Test listing followers of user2
        followers_url = reverse("followers", kwargs={"user_id": self.user2.pk})
        response = self.client.get(followers_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

        # Test listing following of user1
        following_url = reverse("following", kwargs={"user_id": self.user1.pk})
        response = self.client.get(following_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    # ==========================================
    # BOOKMARK TESTS
    # ==========================================

    def test_list_and_create_bookmarks(self):
        url = reverse("list-create-bookmarks")
        self.authenticate_user1()

        # Test Create (Assuming your Bookmark model requires a 'url' or text field, adapt data accordingly)
        data = {"tweet": self.tweet.id}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Test List isolation (user1 should see their bookmark, user2 should see 0 items)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_destroy_bookmark_owner_permission(self):
        # Create a bookmark belonging to user2
        bookmark = Bookmark.objects.create(user=self.user2, tweet=self.tweet)
        url = reverse("destroy-bookmark", kwargs={"pk": bookmark.pk})

        # Try to delete it as user1 (Should fail due to IsOwnerBookmarkPermission)
        self.authenticate_user1()
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Delete it as the true owner (user2)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token2.access_token}")
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Bookmark.objects.filter(pk=bookmark.pk).exists())
