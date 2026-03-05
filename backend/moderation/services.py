from typing import Optional, Union

from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError
from django.db.models import Model

from backend.account.models import User
from backend.moderation.choices import ReportStatus
from backend.moderation.models import Report, ReportReason
from backend.room.models import Room
from backend.access.models import Participant
from backend.core.forms import ReportForm
from backend.core.exceptions import (
    FormValidationException,
    PermissionException,
    ConflictException,
)


class ReportService:
    """Service for report mutation operations."""

    @staticmethod
    def _check_report_permission(reporter: User, target: Model) -> None:
        """Raise PermissionException if reporter is not allowed to report target."""
        if isinstance(target, Room):
            if not Participant.objects.filter(user=reporter, room=target).exists():
                raise PermissionException(
                    "You must be a participant of the room to report it."
                )
        # For User targets (and any future model) any authenticated reporter is allowed.

    @staticmethod
    def create_report(
        reporter: User,
        target: Model,
        reason: ReportReason,
        body: str,
    ) -> Report:
        """
        Create a report for any reportable target (Room, User, …).

        Args:
            reporter: User creating the report
            target: The object being reported
            reason: The ReportReason instance
            body: Detailed description of the report

        Returns:
            The created Report instance

        Raises:
            PermissionException: If the reporter is not allowed to report this target,
                or if the reason is inactive / not valid for this content type
            ConflictException: If an active report already exists for this target
            FormValidationException: If form validation fails
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

        if Report.active_reports(
            user=reporter, content_type=content_type, object_id=target.pk
        ).exists():
            raise ConflictException(
                "You already have an active report targeting this content."
            )

        form = ReportForm(data={"body": body})

        if not form.is_valid():
            raise FormValidationException("Invalid report data", errors=form.errors)

        try:
            report = form.save(commit=False)
            report.user = reporter
            report.content_type = content_type
            report.object_id = target.pk
            report.reason = reason
            report.save()
        except IntegrityError as e:
            raise ConflictException("Could not create report due to a conflict.") from e

        return report

    @staticmethod
    def update_report_status(
        moderator: User,
        report: Report,
        new_status: ReportStatus,
        moderator_note: Optional[str] = None,
    ) -> Report:
        """
        Update a report's status (moderator action).

        Args:
            moderator: User performing the action (must be staff/moderator)
            report: The report to update
            new_status: The new status
            moderator_note: Optional note from the moderator

        Returns:
            The updated Report instance

        Raises:
            PermissionException: If user is not a moderator
        """
        # Defense-in-depth: Even though API layer checks staff/superuser status,
        # we enforce it here as well to prevent accidental service layer misuse.
        if not (moderator.is_staff or moderator.is_superuser):
            raise PermissionException("Only moderators can update report status.")

        report.status = new_status
        report.moderator = moderator

        if moderator_note is not None:
            report.moderator_note = moderator_note

        report.save()

        return report

    @staticmethod
    def resolve_report(
        moderator: User,
        report: Report,
        moderator_note: Optional[str] = None,
    ) -> Report:
        """
        Resolve a report.

        Args:
            moderator: User performing the action (must be staff/moderator)
            report: The report to resolve
            moderator_note: Optional note from the moderator

        Returns:
            The resolved Report instance

        Raises:
            PermissionException: If user is not a moderator
        """
        return ReportService.update_report_status(
            moderator, report, Report.Status.RESOLVED, moderator_note
        )

    @staticmethod
    def dismiss_report(
        moderator: User,
        report: Report,
        moderator_note: Optional[str] = None,
    ) -> Report:
        """
        Dismiss a report.

        Args:
            moderator: User performing the action (must be staff/moderator)
            report: The report to dismiss
            moderator_note: Optional note from the moderator

        Returns:
            The dismissed Report instance

        Raises:
            PermissionException: If user is not a moderator
        """
        return ReportService.update_report_status(
            moderator, report, Report.Status.DISMISSED, moderator_note
        )

    @staticmethod
    def mark_under_review(
        moderator: User,
        report: Report,
        moderator_note: Optional[str] = None,
    ) -> Report:
        """
        Mark a report as under review.

        Args:
            moderator: User performing the action (must be staff/moderator)
            report: The report to mark
            moderator_note: Optional note from the moderator

        Returns:
            The report marked as under review

        Raises:
            PermissionException: If user is not a moderator
        """
        return ReportService.update_report_status(
            moderator, report, Report.Status.UNDER_REVIEW, moderator_note
        )
