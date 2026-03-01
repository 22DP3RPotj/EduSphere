import pytest
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from backend.account.models import User, UserBan
from backend.account.services import RestrictionService


pytestmark = pytest.mark.unit


class RestrictionServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            name="Test User",
            password="testpass123",
        )
        self.admin = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            name="Admin User",
            password="adminpass123",
        )

    def test_ban_user_success(self):
        reason = "Violation of TOS"
        ban = RestrictionService.ban_user(self.user, self.admin, reason)

        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)
        self.assertTrue(ban.is_active)
        self.assertEqual(ban.user, self.user)
        self.assertEqual(ban.banned_by, self.admin)
        self.assertEqual(ban.reason, reason)

    def test_ban_user_self_ban_fails(self):
        with self.assertRaisesMessage(ValidationError, "Users cannot ban themselves"):
            RestrictionService.ban_user(self.admin, self.admin, "Self ban")

    def test_ban_user_with_expiration(self):
        expires_at = timezone.now() + timezone.timedelta(days=1)
        ban = RestrictionService.ban_user(self.user, self.admin, "Temp ban", expires_at)

        self.assertEqual(ban.expires_at, expires_at)

    def test_unban_user_success(self):
        # First ban the user
        RestrictionService.ban_user(self.user, self.admin, "Ban")
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)

        # Unban
        RestrictionService.unban_user(self.user)

        # Verify
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)
        self.assertFalse(
            UserBan.objects.filter(user=self.user, is_active=True).exists()
        )
