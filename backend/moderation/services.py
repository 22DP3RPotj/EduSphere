from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import transaction, IntegrityError
from django.db.models import Model

from backend.account.models import User
from backend.moderation.choices import ActionChoices, CaseStatusChoices
from backend.moderation.models import (
    ModerationAction,
    ModerationCase,
    Report,
    ReportReason,
)
from backend.room.models import Room
from backend.messaging.models import Message
from backend.access.models import Participant
from backend.core.forms import ReportForm
from backend.core.exceptions import (
    FormValidationException,
    PermissionException,
    ConflictException,
)

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
        if isinstance(target, Room):
            if not Participant.objects.filter(user=reporter, room=target).exists():
                raise PermissionException(
                    "You must be a participant of the room to report it."
                )
        elif isinstance(target, Message):
            if not Participant.objects.filter(user=reporter, room=target.room).exists():
                raise PermissionException(
                    "You must be a participant of the room to report a message in it."
                )
        # For User targets (and any future model) any authenticated reporter is allowed.

    @staticmethod
    def create_report(
        reporter: User,
        target: Model,
        reason: ReportReason,
        description: str,
    ) -> Report:
        """
        Create a report for any reportable target (Room, User, …).
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

        form = ReportForm(data={"description": description})
        if not form.is_valid():
            raise FormValidationException("Invalid report data", errors=form.errors)

        with transaction.atomic():
            case = (
                ModerationCase.objects.select_for_update()
                .filter(
                    content_type=content_type,
                    object_id=target.pk,
                    status__in=CaseStatusChoices.active(),
                )
                .first()
            )
            if case is None:
                try:
                    case = ModerationCase.objects.create(
                        content_type=content_type,
                        object_id=target.pk,
                        status=CaseStatusChoices.PENDING,
                    )
                except (IntegrityError, ValidationError):
                    case = (
                        ModerationCase.objects.select_for_update()
                        .filter(
                            content_type=content_type,
                            object_id=target.pk,
                            status__in=CaseStatusChoices.active(),
                        )
                        .get()
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

            report = form.save(commit=False)
            report.reporter = reporter
            report.content_type = content_type
            report.object_id = target.pk
            report.reason = reason
            report.case = case
            report.save()
        return report

    @staticmethod
    def take_case_action(
        moderator: User,
        case: ModerationCase,
        action: ActionChoices,
        note: str = "",
    ) -> ModerationCase:
        """
        Record a moderation action against a case and transition its status.

        The case status is derived from the action:
          - NO_VIOLATION  → DISMISSED
          - All others    → RESOLVED

        Raises:
            PermissionException: If user is not staff or superuser
        """
        if not (moderator.is_staff or moderator.is_superuser):
            raise PermissionException("Only moderators can take case actions.")
        try:
            with transaction.atomic():
                ModerationAction.objects.create(
                    case=case,
                    moderator=moderator,
                    action=action,
                    note=note,
                )

                case.status = ReportService._case_status_for_action(action)
                case.save(update_fields=["status", "updated_at"])
        except IntegrityError as e:
            raise ConflictException("Could not take action due to a conflict.") from e

        return case

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
        if not (moderator.is_staff or moderator.is_superuser):
            raise PermissionException("Only moderators can update case status.")

        case.status = CaseStatusChoices.UNDER_REVIEW
        case.save(update_fields=["status", "updated_at"])

        return case
