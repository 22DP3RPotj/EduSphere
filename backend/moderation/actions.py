from typing import Optional

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import Model

from backend.account.models import User
from backend.core.exceptions import ConflictException, FormValidationException
from backend.moderation.choices import ActionChoices, CaseStatusChoices
from backend.moderation.forms import ModerationActionForm, ReportForm
from backend.moderation.models import ModerationCase, Report, ReportReason


def create_report(
    reporter: User,
    target: Model,
    reason: ReportReason,
    description: Optional[str] = None,
) -> Report:
    content_type = ContentType.objects.get_for_model(target)

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


def take_case_action(
    moderator: User,
    case: ModerationCase,
    action: ActionChoices,
    status: CaseStatusChoices,
    note: Optional[str] = None,
) -> ModerationCase:
    try:
        with transaction.atomic():
            form = ModerationActionForm(data={"note": note})
            if not form.is_valid():
                raise FormValidationException(
                    "Invalid moderation action data", errors=form.errors
                )

            moderation_action = form.save(commit=False)
            moderation_action.case = case
            moderation_action.moderator = moderator
            moderation_action.action = action
            moderation_action.save()

            case.update_status(status)
    except IntegrityError as e:
        raise ConflictException("Could not take action due to a conflict.") from e

    return case


def set_case_under_review(case: ModerationCase) -> ModerationCase:
    case.update_status(CaseStatusChoices.UNDER_REVIEW)
    return case
