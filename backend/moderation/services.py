from typing import Optional

from django.contrib.contenttypes.models import ContentType
from django.db.models import Model

from backend.account.models import User
from backend.account.rules.labels import AccountPermission
from backend.moderation.choices import (
    ActionChoices,
    ActionPriorityChoices,
    CaseStatusChoices,
)
from backend.moderation.models import ModerationCase, Report, ReportReason
from backend.room.models import Room
from backend.messaging.models import Message
from backend.core.exceptions import PermissionException, ConflictException
from backend.moderation.rules.labels import ModerationPermission
from backend.moderation import actions
from backend.room.rules.labels import RoomPermission


_ACTION_TO_STATUS: dict[ActionChoices, CaseStatusChoices] = {
    ActionChoices.NO_VIOLATION: CaseStatusChoices.DISMISSED,
    ActionChoices.CONTENT_REMOVED: CaseStatusChoices.RESOLVED,
    ActionChoices.WARNING: CaseStatusChoices.RESOLVED,
    ActionChoices.TEMP_BAN: CaseStatusChoices.RESOLVED,
    ActionChoices.PERM_BAN: CaseStatusChoices.RESOLVED,
}


class ReportService:
    """Service for report and moderation case operations."""

    @staticmethod
    def _case_status_for_action(action: ActionChoices) -> CaseStatusChoices:
        if action not in _ACTION_TO_STATUS:
            raise ValueError(
                f"No case status mapping defined for action '{action}'. "
                f"Add it to _ACTION_TO_STATUS in services.py."
            )
        return _ACTION_TO_STATUS[action]

    @staticmethod
    def _check_report_permission(reporter: User, target: Model) -> None:
        """Raise PermissionException if reporter is not allowed to report target."""
        if isinstance(target, User):
            if not reporter.has_perm(AccountPermission.VIEW, target):
                raise PermissionException(
                    "You don't have permission to report this user."
                )
        elif isinstance(target, Room):
            if not reporter.has_perm(RoomPermission.VIEW, target):
                raise PermissionException(
                    "You don't have permission to report this room."
                )
        elif isinstance(target, Message):
            if not reporter.has_perm(RoomPermission.VIEW, target.room):
                raise PermissionException(
                    "You don't have permission to report this message."
                )
        else:
            raise ValueError(f"Unsupported target type: {type(target).__name__}. ")

    @staticmethod
    def create_report(
        reporter: User,
        target: Model,
        reason: ReportReason,
        description: Optional[str] = None,
    ) -> Report:
        """
        Create a report for any reportable target (Room, User, Message).
        Automatically gets or creates an active ModerationCase for the target.

        The duplicate check is intentionally kept only here (not inside actions.create_report)
        as a fast-path guard before entering the transaction. The atomic block in
        actions.create_report handles the race condition on case creation via
        select_for_update, but duplicate report detection does not need to be repeated
        inside the transaction since the case lock is already held at that point.

        Raises:
            PermissionException: Reporter lacks access, or reason is invalid for target
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

        if Report.objects.filter(
            reporter=reporter,
            content_type=content_type,
            object_id=target.pk,
            case__status__in=CaseStatusChoices.active(),
        ).exists():
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

        The case status is derived from the action via _ACTION_TO_STATUS. Adding a
        new ActionChoice without a corresponding entry there will raise ValueError.

        Raises:
            PermissionException: If moderator lacks ACT permission on the case
            ConflictException: If the case is not in an actionable state
            ValueError: If action has no status mapping defined
        """
        if not moderator.has_perm(ModerationPermission.ACT, case):
            raise PermissionException("You don't have permission to take case actions.")

        if case.status not in CaseStatusChoices.active():
            raise ConflictException(
                "Actions can only be taken on active (pending or under review) cases."
            )

        status = ReportService._case_status_for_action(action)
        return actions.take_case_action(
            moderator=moderator,
            case=case,
            action=action,
            status=status,
            note=note,
        )

    @staticmethod
    def set_case_priority(
        moderator: User,
        case: ModerationCase,
        priority: ActionPriorityChoices,
    ) -> ModerationCase:
        """
        Update the priority of a case without changing its status.
        Can be called on any case regardless of status.

        Raises:
            PermissionException: If moderator lacks ACT permission on the case
        """
        if not moderator.has_perm(ModerationPermission.ACT, case):
            raise PermissionException(
                "You don't have permission to update case priority."
            )

        return actions.set_case_priority(case=case, priority=priority)

    @staticmethod
    def set_case_under_review(
        moderator: User,
        case: ModerationCase,
    ) -> ModerationCase:
        """
        Transition a PENDING case to UNDER_REVIEW without creating a ModerationAction.

        Raises:
            PermissionException: If moderator lacks REVIEW permission on the case
            ConflictException: If the case is not in PENDING status
        """
        if not moderator.has_perm(ModerationPermission.REVIEW, case):
            raise PermissionException(
                "You don't have permission to update case status."
            )

        if case.status != CaseStatusChoices.PENDING:
            raise ConflictException("Only pending cases can be moved to under review.")

        return actions.set_case_under_review(case=case)

    @staticmethod
    def reopen_case(
        moderator: User,
        case: ModerationCase,
    ) -> ModerationCase:
        """
        Reopen a resolved or dismissed case, resetting it to PENDING.
        Useful when new context emerges or a wrong call needs correcting.

        Raises:
            PermissionException: If moderator lacks ACT permission on the case
            ConflictException: If the case is not in a terminal state
        """
        if not moderator.has_perm(ModerationPermission.ACT, case):
            raise PermissionException("You don't have permission to reopen cases.")

        if case.status not in CaseStatusChoices.finalized():
            raise ConflictException("Only resolved or dismissed cases can be reopened.")

        return actions.reopen_case(case=case)
