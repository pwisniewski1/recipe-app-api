from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from app.utils_test import TestConstants
from core.models import User


def create_user(**kwargs):
    return get_user_model().objects.create_user(**kwargs)


DEFAULT_USER_DETAILS = {
    "email": TestConstants.EMAIL,
    "password": TestConstants.PASSWORD,
    "name": TestConstants.USERNAME,
}
ME_URL = reverse("user:me")


class PublicUserApiTests(TestCase):
    CREATE_USER_URL = reverse("user:create")
    TOKEN_URL = reverse("user:token")

    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        payload = DEFAULT_USER_DETAILS
        res = self.client.post(PublicUserApiTests.CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload["email"])
        self.assertTrue(user.check_password(payload["password"]))
        self.assertNotIn("password", res.data)

    def test_user_with_email_exists_error(self):
        payload = DEFAULT_USER_DETAILS
        create_user(**payload)
        res = self.client.post(PublicUserApiTests.CREATE_USER_URL, payload)
        self.assertGreaterEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        payload = {"email": TestConstants.EMAIL, "password": "dsa", "name": TestConstants.USERNAME}
        res = self.client.post(PublicUserApiTests.CREATE_USER_URL, payload)
        user_exists = get_user_model().objects.filter(email=payload["email"]).exists()
        self.assertGreaterEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        user_details = DEFAULT_USER_DETAILS
        create_user(**user_details)
        payload = {
            "email": user_details["email"],
            "password": user_details["password"],
        }
        res = self.client.post(PublicUserApiTests.TOKEN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("token", res.data)

    def create_token_bad_credentials(self):
        user_details = DEFAULT_USER_DETAILS
        create_user(**user_details)
        payload = {"email": TestConstants.EMAIL, "password": "wrong_password"}
        res = self.client.post(PublicUserApiTests.TOKEN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("token", res.data)

    def test_create_token_blank_password(self):
        user_details = DEFAULT_USER_DETAILS
        create_user(**user_details)
        payload = {"email": TestConstants.EMAIL, "password": ""}
        res = self.client.post(PublicUserApiTests.TOKEN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("token", res.data)

    def test_create_token_no_email(self):
        user_details = DEFAULT_USER_DETAILS
        create_user(**user_details)
        payload = {"email": "", "password": TestConstants.PASSWORD}
        res = self.client.post(PublicUserApiTests.TOKEN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("token", res.data)

    def test_retrieve_user_unauthorized(self):
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    def setUp(self):
        self.user: User = create_user(
            email=TestConstants.EMAIL, password=TestConstants.PASSWORD, name=TestConstants.USERNAME
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in user"""
        res = self.client.get(ME_URL)
        expected_response = {"name": TestConstants.USERNAME, "email": TestConstants.EMAIL}
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, expected_response)

    def test_post_me_not_allowed(self):
        """Test POST is not allowed for ME endpoint"""
        res = self.client.post(ME_URL, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test update user profile for auth user"""
        payload = {"name": "Updated name", "email": "updated_mail@example.com", "password": "myNewPassword124"}
        # check if email can be updated
        res = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.name, payload["name"])
        self.assertTrue(self.user.check_password(payload["password"]))
        self.assertEqual(self.user.email, payload["email"])
