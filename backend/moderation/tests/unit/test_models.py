from django.contrib.auth import get_user_model
from django.test import TestCase

import pytest

pytestmark = pytest.mark.unit

from backend.moderation.models import Report
from backend.room.models import Room

User = get_user_model()


class ReportModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            name="User",
            username="user",
            email="user@email.com",
        )
        self.moderator = User.objects.create_user(
            name="Moderator",
            username="moderator",
            email="moderator@email.com",
            is_staff=True,
            is_superuser=True,
        )
        self.room = Room.objects.create(
            host=self.user,
            name="Test Room",
            description="",
            visibility=Room.Visibility.PUBLIC,
        )

    def test_report_creation(self):
        report = Report.objects.create(
            user=self.user,
            room=self.room,
            reason=Report.Reason.SPAM,
            body="This is spam",
            status=Report.Status.PENDING,
        )
        self.assertEqual(report.status, Report.Status.PENDING)
        self.assertTrue(report.is_active_report)

    def test_report_active_reports(self):
        Report.objects.create(
            user=self.user,
            room=self.room,
            reason=Report.Reason.SPAM,
            body="Spam",
            status=Report.Status.PENDING,
        )
        Report.objects.create(
            user=self.user,
            room=self.room,
            reason=Report.Reason.HARASSMENT,
            body="Harassment",
            status=Report.Status.RESOLVED,
        )
        active = Report.active_reports()
        self.assertEqual(active.count(), 1)

    def test_report_str(self):
        report = Report.objects.create(
            user=self.user,
            room=self.room,
            reason=Report.Reason.SPAM,
            body="Spam",
            status=Report.Status.PENDING,
        )
        self.assertEqual(str(report), "Report by user on Test Room")
