from unittest import mock
import pytest
from django.test import TestCase
from django.utils import timezone
from datetime import datetime, timedelta

from backend.account.models import User, UserBan
from backend.account.tasks import run_expire_user_bans


pytestmark = pytest.mark.unit


class ExpireUserBansTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            name="Test User",
            password="password",
        )
        self.admin = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            name="Admin User",
            password="password",
        )

    @mock.patch("backend.account.tasks.RestrictionService")
    @mock.patch("backend.account.tasks.logger")
    @mock.patch("backend.account.tasks.timezone")
    def test_expire_bans_successful(
        self, mock_timezone, mock_logger, mock_restriction_service
    ):
        """Test that expired bans are correctly identified and lifted."""
        # Setup fixed time
        fixed_now = timezone.make_aware(datetime(2025, 1, 1, 12, 0, 0))
        mock_timezone.now.return_value = fixed_now

        # Create an expired ban
        ban = UserBan.objects.create(
            user=self.user,
            banned_by=self.admin,
            reason="Test ban",
            expires_at=fixed_now - timedelta(hours=1),
            is_active=True,
        )

        # Execute
        count = run_expire_user_bans()

        # Verify
        self.assertEqual(count, 1)
        mock_restriction_service.lift_ban.assert_called_once_with(ban)
        mock_logger.info.assert_any_call("Expired 1 user bans.")

    @mock.patch("backend.account.tasks.RestrictionService")
    @mock.patch("backend.account.tasks.logger")
    def test_expire_bans_handles_service_error(
        self, mock_logger, mock_restriction_service
    ):
        """Test that errors during unbanning are logged and don't stop the process."""
        # Create two expired bans
        user2 = User.objects.create_user(
            username="testuser2",
            email="test2@example.com",
            name="Test User 2",
            password="password",
        )

        UserBan.objects.create(
            user=self.user,
            banned_by=self.admin,
            reason="Test ban 1",
            expires_at=timezone.now() - timedelta(hours=1),
            is_active=True,
        )
        ban = UserBan.objects.create(
            user=user2,
            banned_by=self.admin,
            reason="Test ban 2",
            expires_at=timezone.now() - timedelta(hours=1),
            is_active=True,
        )

        # Service raises error for first user
        mock_restriction_service.lift_ban.side_effect = Exception("Service error")

        # Execute
        with pytest.raises(Exception, match="Service error"):
            run_expire_user_bans()

        # Verify
        mock_restriction_service.lift_ban.assert_called_once_with(ban)
