from graphql import ExecutionResult
from graphql_jwt.testcases import JSONWebTokenTestCase

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
import pytest

pytestmark = pytest.mark.unit

from backend.access.models import Participant, Role
from backend.moderation.models import Report, ReportReason
from backend.room.models import Room, Topic

User = get_user_model()


def make_report(
    user, target, reason, body="Test report body", status=Report.Status.PENDING
):
    ct = ContentType.objects.get_for_model(target)
    return Report.objects.create(
        user=user,
        content_type=ct,
        object_id=target.pk,
        reason=reason,
        body=body,
        status=status,
    )


class ReportMutationsTests(JSONWebTokenTestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            name="TestUser",
            username="testuser",
            email="test@email.com",
        )
        self.moderator = User.objects.create_user(
            name="Moderator",
            username="moderator",
            email="moderator@email.com",
            is_staff=True,
            is_superuser=True,
        )
        self.host = User.objects.create_user(
            name="HostUser",
            username="hostuser",
            email="host@email.com",
        )
        self.room = Room.objects.create(
            host=self.host,
            name="Test Room",
            description="Test Description",
            visibility=Room.Visibility.PUBLIC,
        )
        self.role = Role.objects.create(
            room=self.room, name="Member", description="", priority=0
        )
        self.room.default_role = self.role
        self.room.save()
        Participant.objects.create(user=self.user, room=self.room, role=self.role)

        self.topic = Topic.objects.create(name="TestTopic")
        self.room.topics.add(self.topic)

        self.reason_spam = ReportReason.objects.create(slug="spam", label="Spam")
        self.reason_harassment = ReportReason.objects.create(
            slug="harassment", label="Harassment"
        )

    _create_mutation = """
        mutation CreateReport(
            $targetType: ReportTargetTypeEnum!
            $targetId: UUID!
            $reasonId: UUID!
            $body: String!
        ) {
            createReport(
                targetType: $targetType
                targetId: $targetId
                reasonId: $reasonId
                body: $body
            ) {
                report {
                    id
                    reason { slug }
                    status
                    body
                }
            }
        }
    """

    def test_create_report_room_success(self):
        self.client.authenticate(self.user)
        result: ExecutionResult = self.client.execute(
            self._create_mutation,
            {
                "targetType": "ROOM",
                "targetId": str(self.room.id),
                "reasonId": str(self.reason_spam.id),
                "body": "This room contains spam",
            },
        )
        self.assertIsNone(result.errors)
        data = result.data["createReport"]["report"]
        self.assertEqual(data["reason"]["slug"], "spam")
        self.assertEqual(data["status"], "PENDING")

    def test_create_report_user_success(self):
        self.client.authenticate(self.user)
        result: ExecutionResult = self.client.execute(
            self._create_mutation,
            {
                "targetType": "USER",
                "targetId": str(self.host.id),
                "reasonId": str(self.reason_harassment.id),
                "body": "Harassment by this user",
            },
        )
        self.assertIsNone(result.errors)
        data = result.data["createReport"]["report"]
        self.assertEqual(data["reason"]["slug"], "harassment")

    def test_create_report_not_participant(self):
        non_participant = User.objects.create_user(
            name="NonParticipant",
            username="nonparticipant",
            email="non@email.com",
        )
        self.client.authenticate(non_participant)
        result: ExecutionResult = self.client.execute(
            self._create_mutation,
            {
                "targetType": "ROOM",
                "targetId": str(self.room.id),
                "reasonId": str(self.reason_spam.id),
                "body": "Test report",
            },
        )
        self.assertIsNotNone(result.errors)
        self.assertEqual(result.errors[0].extensions["code"], "PERMISSION_DENIED")

    def test_create_report_already_reported(self):
        make_report(self.user, self.room, self.reason_spam, "Existing report")

        self.client.authenticate(self.user)
        result: ExecutionResult = self.client.execute(
            self._create_mutation,
            {
                "targetType": "ROOM",
                "targetId": str(self.room.id),
                "reasonId": str(self.reason_harassment.id),
                "body": "Another report",
            },
        )
        self.assertIsNotNone(result.errors)
        self.assertEqual(result.errors[0].extensions["code"], "CONFLICT")

    def test_create_report_invalid_reason(self):
        self.client.authenticate(self.user)
        import uuid

        result: ExecutionResult = self.client.execute(
            self._create_mutation,
            {
                "targetType": "ROOM",
                "targetId": str(self.room.id),
                "reasonId": str(uuid.uuid4()),
                "body": "Test",
            },
        )
        self.assertIsNotNone(result.errors)
        self.assertEqual(result.errors[0].extensions["code"], "NOT_FOUND")

    def test_update_report_as_moderator(self):
        report = make_report(self.user, self.room, self.reason_spam)

        self.client.authenticate(self.moderator)
        mutation = """
            mutation UpdateReport($reportId: UUID!, $status: ReportStatus, $moderatorNote: String) {
                updateReport(reportId: $reportId, status: $status, moderatorNote: $moderatorNote) {
                    report {
                        status
                        moderatorNote
                        moderator { username }
                    }
                }
            }
        """
        result: ExecutionResult = self.client.execute(
            mutation,
            {
                "reportId": str(report.id),
                "status": "RESOLVED",
                "moderatorNote": "Issue resolved",
            },
        )
        self.assertIsNone(result.errors)
        data = result.data["updateReport"]["report"]
        self.assertEqual(data["status"], "RESOLVED")
        self.assertEqual(data["moderatorNote"], "Issue resolved")
        self.assertEqual(data["moderator"]["username"], "moderator")

    def test_delete_report_as_moderator(self):
        report = make_report(self.user, self.room, self.reason_spam)

        self.client.authenticate(self.moderator)
        mutation = """
            mutation DeleteReport($reportId: UUID!) {
                deleteReport(reportId: $reportId) {
                    success
                }
            }
        """
        result: ExecutionResult = self.client.execute(
            mutation, {"reportId": str(report.id)}
        )
        self.assertIsNone(result.errors)
        self.assertTrue(result.data["deleteReport"]["success"])
        self.assertFalse(Report.objects.filter(id=report.id).exists())


class ReportQueryTests(JSONWebTokenTestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            name="TestUser",
            username="testuser",
            email="test@email.com",
        )
        self.moderator = User.objects.create_user(
            name="Moderator",
            username="moderator",
            email="moderator@email.com",
            is_staff=True,
            is_superuser=True,
        )
        self.host = User.objects.create_user(
            name="HostUser",
            username="hostuser",
            email="host@email.com",
        )
        self.room = Room.objects.create(
            host=self.host,
            name="Test Room",
            description="Test Description",
        )

        self.reason_spam = ReportReason.objects.create(slug="spam", label="Spam")
        self.reason_harassment = ReportReason.objects.create(
            slug="harassment", label="Harassment"
        )

        self.report1 = make_report(
            self.user, self.room, self.reason_spam, "First report"
        )
        self.report2 = make_report(
            self.user,
            self.host,
            self.reason_harassment,
            "Second report",
            status=Report.Status.RESOLVED,
        )

    def test_submitted_reports(self):
        self.client.authenticate(self.user)
        query = """
            query {
                submittedReports {
                    reason { slug }
                    body
                    status
                }
            }
        """
        result: ExecutionResult = self.client.execute(query)
        self.assertIsNone(result.errors)
        self.assertEqual(len(result.data["submittedReports"]), 2)

    def test_report_detail(self):
        self.client.authenticate(self.user)
        query = """
            query GetReport($reportId: UUID!) {
                report(reportId: $reportId) {
                    reason { slug }
                    body
                }
            }
        """
        result: ExecutionResult = self.client.execute(
            query, {"reportId": str(self.report1.id)}
        )
        self.assertIsNone(result.errors)
        self.assertEqual(result.data["report"]["reason"]["slug"], "spam")

    def test_reports_as_moderator(self):
        self.client.authenticate(self.moderator)
        query = """
            query {
                reports {
                    reason { slug }
                    status
                }
            }
        """
        result: ExecutionResult = self.client.execute(query)
        self.assertIsNone(result.errors)
        self.assertEqual(len(result.data["reports"]), 2)

    def test_report_reasons_all(self):
        self.client.authenticate(self.user)
        query = """
            query {
                reportReasons {
                    slug
                    label
                    isActive
                }
            }
        """
        result: ExecutionResult = self.client.execute(query)
        self.assertIsNone(result.errors)
        slugs = {r["slug"] for r in result.data["reportReasons"]}
        self.assertIn("spam", slugs)
        self.assertIn("harassment", slugs)

    def test_report_reasons_by_target_type(self):
        from backend.account.models import User as UserModel

        user_ct = ContentType.objects.get_for_model(UserModel)
        user_only = ReportReason.objects.create(
            slug="impersonation", label="Impersonation"
        )
        user_only.allowed_content_types.add(user_ct)

        self.client.authenticate(self.user)
        query = """
            query {
                reportReasons(targetType: USER) {
                    slug
                }
            }
        """
        result: ExecutionResult = self.client.execute(query)
        self.assertIsNone(result.errors)
        slugs = {r["slug"] for r in result.data["reportReasons"]}
        # "spam" and "harassment" have no restrictions so they appear; "impersonation" too
        self.assertIn("impersonation", slugs)
        # Room-only reason should NOT appear
        from backend.room.models import Room as RoomModel

        room_ct = ContentType.objects.get_for_model(RoomModel)
        room_only = ReportReason.objects.create(slug="room-spam", label="Room Spam")
        room_only.allowed_content_types.add(room_ct)

        result2: ExecutionResult = self.client.execute(query)
        self.assertIsNone(result2.errors)
        slugs2 = {r["slug"] for r in result2.data["reportReasons"]}
        self.assertNotIn("room-spam", slugs2)
