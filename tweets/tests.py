from django.core.cache import cache
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from tweets.models import Tweet
from users.models import User


class TweetTests(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username="RaiShahabAthar",
            first_name="Shahab",
            last_name="Athar",
            email="shahab@gmail.com",
            password="1234567890",
        )
        self.tweet = Tweet.objects.create(content="Hello", owner=self.user)

        self.client.force_authenticate(user=self.user)
        pass

    def tearDown(self) -> None:
        cache.clear()

    def test_list(self):
        url = reverse("tweets-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Handle both paginated (dict with "results") and unpaginated (list) responses
        data = response.data.get("results", response.data)

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], self.tweet.id)
        self.assertEqual(data[0]["content"], "Hello")

    def test_list_caching_behavior(self):
        url = reverse("tweets-list")

        # First request: Cache miss -> Hits database
        with self.assertNumQueries(2):  # One from DRF and other is the main query.
            response_1 = self.client.get(url)
            self.assertEqual(response_1.status_code, status.HTTP_200_OK)

        # Second request: Cache hit -> Zero database queries executed
        with self.assertNumQueries(0):
            response_2 = self.client.get(url)
            self.assertEqual(response_2.status_code, status.HTTP_200_OK)
            self.assertEqual(response_1.data, response_2.data)
