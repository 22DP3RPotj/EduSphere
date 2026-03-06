from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

import pytest

pytestmark = pytest.mark.unit

from backend.core.constants import DELETED_USER
from backend.moderation.choices import ActionChoices, CaseStatusChoices
from backend.moderation.models import (
    ModerationAction,
    ModerationCase,
    Report,
    ReportReason,
)
from backend.room.models import Room

User = get_user_model()


class ReportReasonModelTest(TestCase):
    def test_reason_creation(self):
        reason, _ = ReportReason.objects.get_or_create(
            slug="spam", defaults={"label": "Spam"}
        )
        self.assertTrue(reason.is_active)
        self.assertEqual(str(reason), "Spam")

    def test_reason_with_content_type_restriction(self):
        ct = ContentType.objects.get_for_model(Room)
        reason, _ = ReportReason.objects.get_or_create(
            slug="room-only", defaults={"label": "Room Only"}
        )
        reason.allowed_content_types.add(ct)
        self.assertIn(ct, reason.allowed_content_types.all())


class ReportModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            name="User",
            username="user",
            email="user@email.com",
        )
        self.room = Room.objects.create(
            host=self.user,
            name="Test Room",
            description="",
            visibility=Room.Visibility.PUBLIC,
        )
        self.reason, _ = ReportReason.objects.get_or_create(
            slug="spam", defaults={"label": "Spam"}
        )
        self.ct_room = ContentType.objects.get_for_model(Room)
        self.case = ModerationCase.objects.create(
            content_type=self.ct_room,
            object_id=self.room.pk,
            status=CaseStatusChoices.PENDING,
        )

    def _make_report(self, **kwargs):
        defaults = dict(
            reporter=self.user,
            content_type=self.ct_room,
            object_id=self.room.pk,
            reason=self.reason,
            description="Test report description",
            case=self.case,
        )
        defaults.update(kwargs)
        return Report.objects.create(**defaults)

    def test_report_creation(self):
        report = self._make_report()
        self.assertEqual(report.content_object, self.room)
        self.assertEqual(report.case, self.case)

    def test_report_str(self):
        report = self._make_report()
        self.assertEqual(str(report), "Report by user on Test Room")

    def test_report_str_deleted_user(self):
        report = self._make_report()
        # Simulate on_delete=SET_NULL by bypassing full_clean via update()
        Report.objects.filter(pk=report.pk).update(reporter=None)
        report.refresh_from_db()
        self.assertIn(DELETED_USER, str(report))


class ModerationCaseModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            name="User",
            username="user",
            email="user@email.com",
        )
        self.room = Room.objects.create(
            host=self.user,
            name="Test Room",
            description="",
            visibility=Room.Visibility.PUBLIC,
        )
        self.ct_room = ContentType.objects.get_for_model(Room)

    def test_case_creation(self):
        case = ModerationCase.objects.create(
            content_type=self.ct_room,
            object_id=self.room.pk,
            status=CaseStatusChoices.PENDING,
        )
        self.assertEqual(case.status, CaseStatusChoices.PENDING)

    def test_unique_active_case_per_target(self):
        from django.core.exceptions import ValidationError

        ModerationCase.objects.create(
            content_type=self.ct_room,
            object_id=self.room.pk,
            status=CaseStatusChoices.PENDING,
        )
        with self.assertRaises(ValidationError):
            ModerationCase.objects.create(
                content_type=self.ct_room,
                object_id=self.room.pk,
                status=CaseStatusChoices.UNDER_REVIEW,
            )

    def test_resolved_case_allows_new_pending(self):
        case = ModerationCase.objects.create(
            content_type=self.ct_room,
            object_id=self.room.pk,
            status=CaseStatusChoices.PENDING,
        )
        case.status = CaseStatusChoices.RESOLVED
        case.save()
        # A new active case for the same target should now be allowed
        new_case = ModerationCase.objects.create(
            content_type=self.ct_room,
            object_id=self.room.pk,
            status=CaseStatusChoices.PENDING,
        )
        self.assertIsNotNone(new_case.pk)


class ModerationActionModelTest(TestCase):
    def setUp(self):
        self.moderator = User.objects.create_user(
            name="Moderator",
            username="moderator",
            email="moderator@email.com",
            is_staff=True,
        )
        self.user = User.objects.create_user(
            name="User",
            username="user",
            email="user@email.com",
        )
        self.room = Room.objects.create(
            host=self.user,
            name="Test Room",
            description="",
            visibility=Room.Visibility.PUBLIC,
        )
        self.ct_room = ContentType.objects.get_for_model(Room)
        self.case = ModerationCase.objects.create(
            content_type=self.ct_room,
            object_id=self.room.pk,
        )

    def test_action_creation(self):
        action = ModerationAction.objects.create(
            case=self.case,
            moderator=self.moderator,
            action=ActionChoices.WARNING,
            note="First warning issued",
        )
        self.assertEqual(action.action, ActionChoices.WARNING)
        self.assertEqual(action.moderator, self.moderator)

    def test_actions_ordered_by_created_at(self):
        ModerationAction.objects.create(
            case=self.case, moderator=self.moderator, action=ActionChoices.WARNING
        )
        ModerationAction.objects.create(
            case=self.case,
            moderator=self.moderator,
            action=ActionChoices.CONTENT_REMOVED,
        )
        actions = list(self.case.actions.values_list("action", flat=True))
        self.assertEqual(
            actions, [ActionChoices.WARNING, ActionChoices.CONTENT_REMOVED]
        )
