import pytest
from django.test import TestCase
from django.utils import timezone
from backend.account.models import User, UserBan
from backend.account.services import ModerationService
from backend.core.exceptions import ValidationException


pytestmark = pytest.mark.unit


class AccountServiceTests(TestCase):
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
        ban = ModerationService.ban_user(
            user=self.user, banned_by=self.admin, reason=reason
        )

        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)
        self.assertTrue(ban.is_active)
        self.assertEqual(ban.user, self.user)
        self.assertEqual(ban.banned_by, self.admin)
        self.assertEqual(ban.reason, reason)

    def test_ban_user_self_ban_fails(self):
        with self.assertRaisesMessage(ValidationException, "You cannot ban yourself."):
            ModerationService.ban_user(
                user=self.admin, banned_by=self.admin, reason="Self ban"
            )

    def test_ban_user_with_expiration(self):
        expires_at = timezone.now() + timezone.timedelta(days=1)
        ban = ModerationService.ban_user(
            user=self.user,
            banned_by=self.admin,
            reason="Temp ban",
            expires_at=expires_at,
        )

        self.assertEqual(ban.expires_at, expires_at)

    def test_unban_user_success(self):
        # First ban the user
        ModerationService.ban_user(
            user=self.user, banned_by=self.admin, reason="Temp ban"
        )
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)

        # Unban
        ModerationService.unban_user(actor=self.admin, user=self.user)

        # Verify
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)
        self.assertFalse(
            UserBan.objects.filter(user=self.user, is_active=True).exists()
        )
