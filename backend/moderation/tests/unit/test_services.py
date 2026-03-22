import pytest

pytestmark = [pytest.mark.unit, pytest.mark.services]

from django.contrib.contenttypes.models import ContentType

from backend.core.exceptions import (
    ConflictException,
    PermissionException,
)
from backend.moderation.choices import ActionChoices, CaseStatusChoices
from backend.moderation.models import (
    ModerationAction,
    ReportReason,
)
from backend.moderation.services import ReportService
from backend.core.tests.service_base import ServiceTestBase


class ReportServiceTest(ServiceTestBase):
    """Test ReportService methods."""

    def setUp(self):
        super().setUp()
        self.reason_spam, _ = ReportReason.objects.get_or_create(
            slug="spam", defaults={"label": "Spam"}
        )
        self.reason_harassment, _ = ReportReason.objects.get_or_create(
            slug="harassment", defaults={"label": "Harassment"}
        )

    # --- Room target tests ---

    def test_create_report_room_success(self):
        self._add_member(self.member, self.member_role)

        report = ReportService.create_report(
            reporter=self.member,
            target=self.room,
            reason=self.reason_spam,
            description="This room contains inappropriate content",
        )

        self.assertEqual(report.reporter, self.member)
        self.assertEqual(report.content_object, self.room)
        self.assertEqual(report.reason, self.reason_spam)
        self.assertIsNotNone(report.case)
        self.assertEqual(report.case.status, CaseStatusChoices.PENDING)

    def test_create_report_not_participant(self):
        self.room.visibility = self.room.Visibility.PRIVATE
        self.room.save(update_fields=["visibility"])

        with self.assertRaises(PermissionException):
            ReportService.create_report(
                reporter=self.other_user,
                target=self.room,
                reason=self.reason_spam,
                description="Spam",
            )

    def test_create_report_active_exists(self):
        self._add_member(self.member, self.member_role)

        ReportService.create_report(
            reporter=self.member,
            target=self.room,
            reason=self.reason_spam,
            description="First report",
        )

        with self.assertRaises(ConflictException):
            ReportService.create_report(
                reporter=self.member,
                target=self.room,
                reason=self.reason_spam,
                description="Second report",
            )

    def test_create_report_reuses_active_case(self):
        """Two reports on the same target share the same ModerationCase."""
        self._add_member(self.member, self.member_role)
        self._add_member(self.other_user, self.member_role)

        report1 = ReportService.create_report(
            reporter=self.member,
            target=self.room,
            reason=self.reason_spam,
            description="First reporter",
        )
        report2 = ReportService.create_report(
            reporter=self.other_user,
            target=self.room,
            reason=self.reason_harassment,
            description="Second reporter",
        )

        self.assertEqual(report1.case, report2.case)

    # --- User target tests ---

    def test_create_report_user_success(self):
        report = ReportService.create_report(
            reporter=self.member,
            target=self.other_user,
            reason=self.reason_harassment,
            description="Harassing other users",
        )

        self.assertEqual(report.reporter, self.member)
        self.assertEqual(report.content_object, self.other_user)
        self.assertEqual(report.reason, self.reason_harassment)

    def test_create_report_user_no_participant_check(self):
        """Any authenticated user can report another user without membership."""
        report = ReportService.create_report(
            reporter=self.other_user,
            target=self.member,
            reason=self.reason_spam,
            description="Suspicious user",
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
                description="Test",
            )

    def test_create_report_reason_wrong_content_type(self):
        """A reason scoped only to User targets should be rejected for a Room."""
        from backend.account.models import User as UserModel

        user_ct = ContentType.objects.get_for_model(UserModel)
        user_only_reason, _ = ReportReason.objects.get_or_create(
            slug="impersonation", defaults={"label": "Impersonation"}
        )
        user_only_reason.allowed_content_types.add(user_ct)

        self._add_member(self.member, self.member_role)

        with self.assertRaises(PermissionException):
            ReportService.create_report(
                reporter=self.member,
                target=self.room,
                reason=user_only_reason,
                description="Impersonation in room?",
            )

    # --- Moderator action tests ---

    def test_take_case_action_resolves_case(self):
        self._add_member(self.member, self.member_role)

        report = ReportService.create_report(
            reporter=self.member,
            target=self.room,
            reason=self.reason_spam,
            description="Test report",
        )
        case = report.case

        updated_case = ReportService.take_case_action(
            moderator=self.moderator,
            case=case,
            action=ActionChoices.WARNING,
            note="Warning issued",
        )

        self.assertEqual(updated_case.status, CaseStatusChoices.RESOLVED)
        action = ModerationAction.objects.get(case=case)
        self.assertEqual(action.action, ActionChoices.WARNING)
        self.assertEqual(action.moderator, self.moderator)
        self.assertEqual(action.note, "Warning issued")

    def test_take_case_action_no_violation_dismisses(self):
        self._add_member(self.member, self.member_role)

        report = ReportService.create_report(
            reporter=self.member,
            target=self.room,
            reason=self.reason_spam,
            description="Test report",
        )

        updated_case = ReportService.take_case_action(
            moderator=self.moderator,
            case=report.case,
            action=ActionChoices.NO_VIOLATION,
        )

        self.assertEqual(updated_case.status, CaseStatusChoices.DISMISSED)

    def test_take_case_action_not_moderator(self):
        self._add_member(self.member, self.member_role)

        report = ReportService.create_report(
            reporter=self.member,
            target=self.room,
            reason=self.reason_spam,
            description="Test report",
        )

        with self.assertRaises(PermissionException):
            ReportService.take_case_action(
                moderator=self.other_user,
                case=report.case,
                action=ActionChoices.WARNING,
            )

    def test_set_case_under_review_success(self):
        self._add_member(self.member, self.member_role)

        report = ReportService.create_report(
            reporter=self.member,
            target=self.room,
            reason=self.reason_spam,
            description="Test report",
        )

        updated_case = ReportService.set_case_under_review(
            moderator=self.moderator,
            case=report.case,
        )

        self.assertEqual(updated_case.status, CaseStatusChoices.UNDER_REVIEW)
        self.assertEqual(ModerationAction.objects.filter(case=report.case).count(), 0)

    def test_set_case_under_review_not_moderator(self):
        self._add_member(self.member, self.member_role)

        report = ReportService.create_report(
            reporter=self.member,
            target=self.room,
            reason=self.reason_spam,
            description="Test report",
        )

        with self.assertRaises(PermissionException):
            ReportService.set_case_under_review(
                moderator=self.other_user,
                case=report.case,
            )
