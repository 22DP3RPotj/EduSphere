from typing import Optional

from django.db import IntegrityError

from backend.core.models import Report, User
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
    def create_report(
        reporter: User,
        room: Room,
        reason: Report.ReportReason,
        body: str,
    ) -> Report:
        """
        Create a report for a room.
        
        Args:
            reporter: User creating the report (must be a participant)
            room: The room being reported
            reason: The reason for the report
            body: Detailed description of the report
            
        Returns:
            The created Report instance
            
        Raises:
            PermissionException: If user is not a participant
            ConflictException: If an active report already exists
            FormValidationException: If form validation fails
        """
        if not Participant.objects.filter(user=reporter, room=room).exists():
            raise PermissionException("You must be a participant of the room to report it.")
        
        if Report.active_reports(user=reporter, room=room).exists():
            raise ConflictException("You already have an active report targeting this room.")
        
        data = {
            "reason": reason,
            "body": body,
        }
        
        form = ReportForm(data=data)
        
        if not form.is_valid():
            raise FormValidationException("Invalid report data", errors=form.errors)
        
        try:
            report = form.save(commit=False)
            report.user = reporter
            report.room = room
            report.save()
        except IntegrityError as e:
            raise ConflictException("Could not create report due to a conflict.") from e
    
        return report

    @staticmethod
    def update_report_status(
        moderator: User,
        report: Report,
        new_status: Report.ReportStatus,
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
            moderator,
            report,
            Report.ReportStatus.RESOLVED,
            moderator_note
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
            moderator,
            report,
            Report.ReportStatus.DISMISSED,
            moderator_note
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
            moderator,
            report,
            Report.ReportStatus.UNDER_REVIEW,
            moderator_note
        )
