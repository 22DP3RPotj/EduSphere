from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

import pytest

pytestmark = pytest.mark.unit

from backend.core.constants import DELETED_USER
from backend.moderation.models import Report, ReportReason
from backend.room.models import Room

User = get_user_model()


class ReportReasonModelTest(TestCase):
    def test_reason_creation(self):
        reason = ReportReason.objects.create(slug="spam", label="Spam")
        self.assertTrue(reason.is_active)
        self.assertEqual(str(reason), "Spam")

    def test_reason_with_content_type_restriction(self):
        ct = ContentType.objects.get_for_model(Room)
        reason = ReportReason.objects.create(slug="room-only", label="Room Only")
        reason.allowed_content_types.add(ct)
        self.assertIn(ct, reason.allowed_content_types.all())


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
        self.reason = ReportReason.objects.create(slug="spam", label="Spam")
        self.ct_room = ContentType.objects.get_for_model(Room)

    def _make_report(self, **kwargs):
        defaults = dict(
            user=self.user,
            content_type=self.ct_room,
            object_id=self.room.pk,
            reason=self.reason,
            body="Test report body",
            status=Report.Status.PENDING,
        )
        defaults.update(kwargs)
        return Report.objects.create(**defaults)

    def test_report_creation(self):
        report = self._make_report()
        self.assertEqual(report.status, Report.Status.PENDING)
        self.assertTrue(report.is_active_report)
        self.assertEqual(report.content_object, self.room)

    def test_report_active_reports(self):
        self._make_report()
        reason2 = ReportReason.objects.create(slug="harassment", label="Harassment")
        # Create a resolved report with a unique user so unique constraint is not hit
        other_user = User.objects.create_user(
            name="Other", username="other", email="other@email.com"
        )
        self._make_report(user=other_user, reason=reason2, status=Report.Status.RESOLVED)
        active = Report.active_reports()
        self.assertEqual(active.count(), 1)

    def test_report_str(self):
        report = self._make_report()
        self.assertEqual(str(report), "Report by user on Test Room")

    def test_report_str_deleted_user(self):
        report = self._make_report()
        # Simulate on_delete=SET_NULL by bypassing full_clean via update()
        Report.objects.filter(pk=report.pk).update(user=None)
        report.refresh_from_db()
        self.assertIn(DELETED_USER, str(report))

