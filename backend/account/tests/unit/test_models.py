import pytest
from django.contrib.auth import get_user_model
from django.test import TestCase

pytestmark = pytest.mark.unit

User = get_user_model()


class UserModelTest(TestCase):
    def test_user_creation(self):
        user = User.objects.create_user(
            name="Test User",
            username="testuser",
            email="test@email.com",
            password="testpass123",
        )
        assert user.username == "testuser"
        assert user.email == "test@email.com"
        assert user.is_active
        assert not user.is_staff

    def test_user_slug_conversion(self):
        user = User.objects.create_user(
            name="Test User",
            username="Test User",
            email="test@email.com",
        )
        assert user.username == "test-user"

    def test_user_str(self):
        user = User.objects.create_user(
            name="Test User",
            username="testuser",
            email="test@email.com",
        )
        assert str(user) == "testuser"
