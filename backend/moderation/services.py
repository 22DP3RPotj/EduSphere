from typing import Optional

from django.contrib.contenttypes.models import ContentType
from django.db.models import Model

from backend.account.models import User
from backend.account.rules.labels import AccountPermission
from backend.moderation.choices import ActionChoices, CaseStatusChoices
from backend.moderation.models import ModerationCase, Report, ReportReason
from backend.room.models import Room
from backend.messaging.models import Message
from backend.core.exceptions import PermissionException, ConflictException
from backend.moderation.rules.labels import ModerationPermission
from backend.moderation import actions
from backend.room.rules.labels import RoomPermission

_ACTION_TO_STATUS = {
    ActionChoices.NO_VIOLATION: CaseStatusChoices.DISMISSED,
}


class ReportService:
    """Service for report and moderation case operations."""

    @staticmethod
    def _case_status_for_action(action: ActionChoices) -> CaseStatusChoices:
        return _ACTION_TO_STATUS.get(action, CaseStatusChoices.RESOLVED)

    @staticmethod
    def _check_report_permission(reporter: User, target: Model) -> None:
        """Raise PermissionException if reporter is not allowed to report target."""
        if isinstance(target, User):
            if not reporter.has_perm(AccountPermission.READ, target):
                raise PermissionException(
                    "You don't have permission to report this user."
                )
        elif isinstance(target, Room):
            if not reporter.has_perm(RoomPermission.READ, target):
                raise PermissionException(
                    "You don't have permission to report this room."
                )
        elif isinstance(target, Message):
            if not reporter.has_perm(RoomPermission.READ, target.room):
                raise PermissionException(
                    "You don't have permission to report this message."
                )

    @staticmethod
    def create_report(
        reporter: User,
        target: Model,
        reason: ReportReason,
        description: Optional[str] = None,
    ) -> Report:
        """
        Create a report for any reportable target (Room, User, ...).
        Automatically gets or creates an active ModerationCase for the target.

        Raises:
            PermissionException: Reporter not allowed, or reason invalid for target
            ConflictException: Reporter already has an active report on this target
            FormValidationException: description failed form validation
        """
        ReportService._check_report_permission(reporter, target)

        content_type = ContentType.objects.get_for_model(target)

        if not reason.is_active:
            raise PermissionException("This report reason is no longer available.")

        allowed_cts = reason.allowed_content_types.all()
        if allowed_cts.exists() and not allowed_cts.filter(pk=content_type.pk).exists():
            raise PermissionException(
                "This report reason is not valid for the selected target type."
            )

        active_duplicate = Report.objects.filter(
            reporter=reporter,
            content_type=content_type,
            object_id=target.pk,
            case__status__in=CaseStatusChoices.active(),
        ).exists()
        if active_duplicate:
            raise ConflictException(
                "You already have an active report targeting this content."
            )

        return actions.create_report(
            reporter=reporter,
            target=target,
            reason=reason,
            description=description,
        )

    @staticmethod
    def take_case_action(
        moderator: User,
        case: ModerationCase,
        action: ActionChoices,
        note: Optional[str] = None,
    ) -> ModerationCase:
        """
        Record a moderation action against a case and transition its status.

        The case status is derived from the action:
          - NO_VIOLATION  -> DISMISSED
          - All others    -> RESOLVED

        Raises:
            PermissionException: If user is not staff or superuser
        """
        if not moderator.has_perm(ModerationPermission.ACT, case):
            raise PermissionException("You don't have permission to take case actions.")

        status = ReportService._case_status_for_action(action)
        return actions.take_case_action(
            moderator=moderator,
            case=case,
            action=action,
            status=status,
            note=note,
        )

    @staticmethod
    def set_case_under_review(
        moderator: User,
        case: ModerationCase,
    ) -> ModerationCase:
        """
        Transition a case to UNDER_REVIEW without creating a ModerationAction.

        Raises:
            PermissionException: If user is not staff or superuser
        """
        if not moderator.has_perm(ModerationPermission.REVIEW, case):
            raise PermissionException(
                "You don't have permission to update case status."
            )

        return actions.set_case_under_review(case=case)
