import pytest

pytestmark = [pytest.mark.unit, pytest.mark.services]

from backend.core.exceptions import (
    ConflictException,
    FormValidationException,
    PermissionException,
    ValidationException,
)
from backend.moderation.models import Report
from backend.moderation.services import ReportService
from backend.tests.service_base import ServiceTestBase


class ReportServiceTest(ServiceTestBase):
    """Test ReportService methods."""

    def test_create_report_success(self):
        self._add_member(self.member, self.member_role)

        report = ReportService.create_report(
            reporter=self.member,
            room=self.room,
            reason=Report.Reason.INAPPROPRIATE_CONTENT,
            body="This room contains inappropriate content",
        )

        self.assertEqual(report.user, self.member)
        self.assertEqual(report.room, self.room)
        self.assertEqual(report.reason, Report.Reason.INAPPROPRIATE_CONTENT)
        self.assertEqual(report.status, Report.Status.PENDING)

    def test_create_report_not_participant(self):
        with self.assertRaises(PermissionException):
            ReportService.create_report(
                reporter=self.other_user,
                room=self.room,
                reason=Report.Reason.SPAM,
                body="Spam",
            )

    def test_create_report_invalid_data(self):
        self._add_member(self.member, self.member_role)

        with self.assertRaises((ValidationException, FormValidationException)):
            ReportService.create_report(
                reporter=self.member,
                room=self.room,
                reason=Report.Reason.SPAM,
                body="",
            )

    def test_create_report_active_exists(self):
        self._add_member(self.member, self.member_role)

        ReportService.create_report(
            reporter=self.member,
            room=self.room,
            reason=Report.Reason.SPAM,
            body="First report",
        )

        with self.assertRaises(ConflictException):
            ReportService.create_report(
                reporter=self.member,
                room=self.room,
                reason=Report.Reason.SPAM,
                body="Second report",
            )

    def test_update_report_status_success(self):
        self._add_member(self.member, self.member_role)

        report = ReportService.create_report(
            reporter=self.member,
            room=self.room,
            reason=Report.Reason.SPAM,
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
            room=self.room,
            reason=Report.Reason.SPAM,
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
            room=self.room,
            reason=Report.Reason.SPAM,
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
            room=self.room,
            reason=Report.Reason.SPAM,
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
            room=self.room,
            reason=Report.Reason.SPAM,
            body="Test report",
        )

        review = ReportService.mark_under_review(
            moderator=self.moderator,
            report=report,
            moderator_note="Checking this",
        )

        self.assertEqual(review.status, Report.Status.UNDER_REVIEW)
