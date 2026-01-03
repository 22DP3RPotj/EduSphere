import uuid

from django.test import tag

from backend.core.exceptions import PermissionException
from backend.invite.services import InviteService
from backend.moderation.models import Report
from backend.moderation.services import ReportService
from backend.tests.service_base import ServiceTestBase


@tag("unit", "services", "error-handling")
class ErrorHandlingTests(ServiceTestBase):
    """Test error handling across services."""

    def test_invite_get_by_token_none(self):
        result = InviteService.get_invite_by_token(None)
        self.assertIsNone(result)

    def test_invite_get_by_token_fake_uuid(self):
        result = InviteService.get_invite_by_token(uuid.uuid4())
        self.assertIsNone(result)

    def test_update_report_non_moderator_fails(self):
        self._add_member(self.member, self.member_role)
        report = ReportService.create_report(
            reporter=self.member,
            room=self.room,
            reason=Report.Reason.SPAM,
            body="Test",
        )

        with self.assertRaises(PermissionException):
            ReportService.update_report_status(
                moderator=self.other_user,
                report=report,
                new_status=Report.Status.UNDER_REVIEW,
            )
