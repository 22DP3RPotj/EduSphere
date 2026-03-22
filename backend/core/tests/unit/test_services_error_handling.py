import uuid

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.services, pytest.mark.error_handling]

from backend.core.exceptions import PermissionException
from backend.invite.services import InviteService
from backend.moderation.choices import ActionChoices
from backend.moderation.models import ReportReason
from backend.moderation.services import ReportService
from backend.core.tests.service_base import ServiceTestBase


class ErrorHandlingTests(ServiceTestBase):
    """Test error handling across services."""

    def test_invite_get_by_token_none(self):
        result = InviteService.get_invite_by_token(None)
        self.assertIsNone(result)

    def test_invite_get_by_token_fake_uuid(self):
        result = InviteService.get_invite_by_token(uuid.uuid4())
        self.assertIsNone(result)

    def test_take_case_action_non_moderator_fails(self):
        self._add_member(self.member, self.member_role)
        reason, _ = ReportReason.objects.get_or_create(
            slug="spam", defaults={"label": "Spam"}
        )
        report = ReportService.create_report(
            reporter=self.member,
            target=self.room,
            reason=reason,
            description="Test report content",
        )

        with self.assertRaises(PermissionException):
            ReportService.take_case_action(
                moderator=self.other_user,
                case=report.case,
                action=ActionChoices.WARNING,
            )
