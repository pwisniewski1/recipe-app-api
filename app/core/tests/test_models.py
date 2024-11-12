"""Test custom django models"""

from decimal import Decimal
from typing import List, Any
from django.test import TestCase
from django.contrib.auth import get_user_model
from ..models import User
from core import models
from app.utils_test import TestConstants


def create_user(email=TestConstants.EMAIL, password=TestConstants.PASSWORD):
    return get_user_model().objects.create_user(email, password)


class ModelTest(TestCase):
    """Test models"""

    def test_create_user_with_email_successful(self):
        email = "test@example.com"
        password = "test123!"
        user = get_user_model()
        user = user.objects.create_user(email=email, password=password)
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password), password)

    def test_new_user_email_normalized(self):
        sample_emails: List[List[Any]] = [
            ("test1@EXAmple.com", "test1@example.com"),
            ("Test2@Example.com", "Test2@example.com"),
            ("TEST3@EXAMPLE.com", "TEST3@example.com"),
            ("test4@example.COM", "test4@example.com"),
        ]
        for email, expected_email in sample_emails:
            user = get_user_model()
            user = user.objects.create_user(email=email, password="sample")
            self.assertEqual(user.email, expected_email)

    def test_new_user_without_email_raises_erro(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(email="", password="test123")

    def test_create_superuser(self):
        user: User = get_user_model().objects.create_superuser("test@example.com", "test123")
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_recipe(self):
        """Test create recipe is succesful"""
        user = get_user_model().objects.create_user(email=TestConstants.EMAIL, password=TestConstants.PASSWORD)
        recipe = models.Recipe.objects.create(
            user=user, title="example recipe", time_minutes=5, price=Decimal("5.50"), description="Sample description"
        )
        self.assertEqual(str(recipe), recipe.title)

    def test_create_tag(self):
        """Test creating a tag is successful"""
        user = create_user()
        tag = models.Tag.objects.create(user=user, name=TestConstants.TAG)
        self.assertEqual(str(tag), tag.name)
