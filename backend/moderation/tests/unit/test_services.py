import pytest

pytestmark = [pytest.mark.unit, pytest.mark.services]

from django.contrib.contenttypes.models import ContentType

from backend.core.exceptions import (
    ConflictException,
    FormValidationException,
    PermissionException,
    ValidationException,
)
from backend.moderation.models import Report, ReportReason
from backend.moderation.services import ReportService
from backend.core.tests.service_base import ServiceTestBase


class ReportServiceTest(ServiceTestBase):
    """Test ReportService methods."""

    def setUp(self):
        super().setUp()
        self.reason_spam = ReportReason.objects.create(slug="spam", label="Spam")
        self.reason_harassment = ReportReason.objects.create(
            slug="harassment", label="Harassment"
        )
        self.room_ct = ContentType.objects.get_for_model(self.room)

    # --- Room target tests ---

    def test_create_report_room_success(self):
        self._add_member(self.member, self.member_role)

        report = ReportService.create_report(
            reporter=self.member,
            target=self.room,
            reason=self.reason_spam,
            body="This room contains inappropriate content",
        )

        self.assertEqual(report.user, self.member)
        self.assertEqual(report.content_object, self.room)
        self.assertEqual(report.reason, self.reason_spam)
        self.assertEqual(report.status, Report.Status.PENDING)

    def test_create_report_not_participant(self):
        with self.assertRaises(PermissionException):
            ReportService.create_report(
                reporter=self.other_user,
                target=self.room,
                reason=self.reason_spam,
                body="Spam",
            )

    def test_create_report_invalid_body(self):
        self._add_member(self.member, self.member_role)

        with self.assertRaises((ValidationException, FormValidationException)):
            ReportService.create_report(
                reporter=self.member,
                target=self.room,
                reason=self.reason_spam,
                body="",
            )

    def test_create_report_active_exists(self):
        self._add_member(self.member, self.member_role)

        ReportService.create_report(
            reporter=self.member,
            target=self.room,
            reason=self.reason_spam,
            body="First report",
        )

        with self.assertRaises(ConflictException):
            ReportService.create_report(
                reporter=self.member,
                target=self.room,
                reason=self.reason_spam,
                body="Second report",
            )

    # --- User target tests ---

    def test_create_report_user_success(self):
        report = ReportService.create_report(
            reporter=self.member,
            target=self.other_user,
            reason=self.reason_harassment,
            body="Harassing other users",
        )

        self.assertEqual(report.user, self.member)
        self.assertEqual(report.content_object, self.other_user)
        self.assertEqual(report.reason, self.reason_harassment)

    def test_create_report_user_no_participant_check(self):
        """Any authenticated user can report another user without membership."""
        report = ReportService.create_report(
            reporter=self.other_user,
            target=self.member,
            reason=self.reason_spam,
            body="Suspicious user",
        )
        self.assertIsNotNone(report.pk)

    # --- Reason validation tests ---

    def test_create_report_inactive_reason(self):
        inactive = ReportReason.objects.create(
            slug="old-reason", label="Old", is_active=False
        )
        self._add_member(self.member, self.member_role)

        with self.assertRaises(PermissionException):
            ReportService.create_report(
                reporter=self.member,
                target=self.room,
                reason=inactive,
                body="Test",
            )

    def test_create_report_reason_wrong_content_type(self):
        """A reason scoped only to User targets should be rejected for a Room."""
        from backend.account.models import User as UserModel

        user_ct = ContentType.objects.get_for_model(UserModel)
        user_only_reason = ReportReason.objects.create(
            slug="impersonation", label="Impersonation"
        )
        user_only_reason.allowed_content_types.add(user_ct)

        self._add_member(self.member, self.member_role)

        with self.assertRaises(PermissionException):
            ReportService.create_report(
                reporter=self.member,
                target=self.room,
                reason=user_only_reason,
                body="Impersonation in room?",
            )

    # --- Moderator action tests ---

    def test_update_report_status_success(self):
        self._add_member(self.member, self.member_role)

        report = ReportService.create_report(
            reporter=self.member,
            target=self.room,
            reason=self.reason_spam,
            body="Test report",
        )

        updated = ReportService.update_report_status(
            moderator=self.moderator,
            report=report,
            new_status=Report.Status.UNDER_REVIEW,
            moderator_note="Reviewing this",
        )

        self.assertEqual(updated.status, Report.Status.UNDER_REVIEW)
        self.assertEqual(updated.moderator, self.moderator)
        self.assertEqual(updated.moderator_note, "Reviewing this")

    def test_update_report_status_not_moderator(self):
        self._add_member(self.member, self.member_role)

        report = ReportService.create_report(
            reporter=self.member,
            target=self.room,
            reason=self.reason_spam,
            body="Test report",
        )

        with self.assertRaises(PermissionException):
            ReportService.update_report_status(
                moderator=self.other_user,
                report=report,
                new_status=Report.Status.RESOLVED,
            )

    def test_resolve_report_success(self):
        self._add_member(self.member, self.member_role)

        report = ReportService.create_report(
            reporter=self.member,
            target=self.room,
            reason=self.reason_spam,
            body="Test report",
        )

        resolved = ReportService.resolve_report(
            moderator=self.moderator,
            report=report,
            moderator_note="Action taken",
        )

        self.assertEqual(resolved.status, Report.Status.RESOLVED)

    def test_dismiss_report_success(self):
        self._add_member(self.member, self.member_role)

        report = ReportService.create_report(
            reporter=self.member,
            target=self.room,
            reason=self.reason_spam,
            body="Test report",
        )

        dismissed = ReportService.dismiss_report(
            moderator=self.moderator,
            report=report,
            moderator_note="No action needed",
        )

        self.assertEqual(dismissed.status, Report.Status.DISMISSED)

    def test_mark_under_review_success(self):
        self._add_member(self.member, self.member_role)

        report = ReportService.create_report(
            reporter=self.member,
            target=self.room,
            reason=self.reason_spam,
            body="Test report",
        )

        review = ReportService.mark_under_review(
            moderator=self.moderator,
            report=report,
            moderator_note="Checking this",
        )

        self.assertEqual(review.status, Report.Status.UNDER_REVIEW)
