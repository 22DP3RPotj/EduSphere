from django.contrib.auth import get_user_model
from graphql import ExecutionResult
from graphql_jwt.testcases import JSONWebTokenTestCase

from backend.core.models import Room, Topic, Report

User = get_user_model()


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
            is_superuser=True
        )
        self.room = Room.objects.create(
            host=User.objects.create_user(
                name="HostUser",
                username="hostuser", 
                email="host@email.com",
            ),
            name="Test Room",
            description="Test Description"
        )
        self.room.participants.add(self.user)
        
        self.topic = Topic.objects.create(name="TestTopic")
        self.room.topics.add(self.topic)

    def test_create_report_success(self):
        self.client.authenticate(self.user)
        mutation = """
            mutation CreateReport($roomId: UUID!, $reason: ReportReason!, $body: String!) {
                createReport(roomId: $roomId, reason: $reason, body: $body) {
                    report {
                        id
                        reason
                        status
                        body
                    }
                }
            }
        """
        variables = {
            "roomId": str(self.room.id),
            "reason": "SPAM", 
            "body": "This room contains spam"
        }
        result: ExecutionResult = self.client.execute(mutation, variables)
        self.assertIsNone(result.errors)
        self.assertEqual(result.data["createReport"]["report"]["reason"], "SPAM")
        self.assertEqual(result.data["createReport"]["report"]["status"], "PENDING")
        self.assertTrue(Report.objects.filter(room=self.room, user=self.user).exists())

    def test_create_report_not_participant(self):
        non_participant = User.objects.create_user(
            name="NonParticipant",
            username="nonparticipant",
            email="non@email.com",
        )
        self.client.authenticate(non_participant)
        
        mutation = """
            mutation CreateReport($roomId: UUID!, $reason: ReportReason!, $body: String!) {
                createReport(roomId: $roomId, reason: $reason, body: $body) {
                    report { id }
                }
            }
        """
        variables = {
            "roomId": str(self.room.id),
            "reason": "SPAM",
            "body": "Test report"
        }
        result: ExecutionResult = self.client.execute(mutation, variables)
        self.assertIsNotNone(result.errors)
        self.assertEqual(result.errors[0].extensions["code"], "NOT_PARTICIPANT")

    def test_create_report_already_reported(self):
        Report.objects.create(
            user=self.user,
            room=self.room,
            reason="SPAM",
            body="Existing report"
        )
        
        self.client.authenticate(self.user)
        mutation = """
            mutation CreateReport($roomId: UUID!, $reason: ReportReason!, $body: String!) {
                createReport(roomId: $roomId, reason: $reason, body: $body) {
                    report { id }
                }
            }
        """
        variables = {
            "roomId": str(self.room.id),
            "reason": "HARASSMENT", 
            "body": "Another report"
        }
        result: ExecutionResult = self.client.execute(mutation, variables)
        self.assertIsNotNone(result.errors)
        self.assertEqual(result.errors[0].extensions["code"], "ALREADY_REPORTED")

    def test_update_report_as_moderator(self):
        report = Report.objects.create(
            user=self.user,
            room=self.room,
            reason="SPAM",
            body="Test report"
        )
        
        self.client.authenticate(self.moderator)
        mutation = """
            mutation UpdateReport($reportId: UUID!, $status: ReportStatus!, $moderatorNote: String) {
                updateReport(reportId: $reportId, status: $status, moderatorNote: $moderatorNote) {
                    report {
                        status
                        moderatorNote
                        moderator { username }
                    }
                }
            }
        """
        variables = {
            "reportId": str(report.id),
            "status": "RESOLVED",
            "moderatorNote": "Issue resolved"
        }
        result: ExecutionResult = self.client.execute(mutation, variables)
        self.assertIsNone(result.errors)
        self.assertEqual(result.data["updateReport"]["report"]["status"], "RESOLVED")
        self.assertEqual(result.data["updateReport"]["report"]["moderatorNote"], "Issue resolved")
        self.assertEqual(result.data["updateReport"]["report"]["moderator"]["username"], "moderator")

    def test_delete_report_as_moderator(self):
        report = Report.objects.create(
            user=self.user,
            room=self.room, 
            reason="SPAM",
            body="Test report"
        )
        
        self.client.authenticate(self.moderator)
        mutation = """
            mutation DeleteReport($reportId: UUID!) {
                deleteReport(reportId: $reportId) {
                    success
                }
            }
        """
        variables = {"reportId": str(report.id)}
        result: ExecutionResult = self.client.execute(mutation, variables)
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
            is_superuser=True
        )
        self.room = Room.objects.create(
            host=User.objects.create_user(
                name="HostUser",
                username="hostuser",
                email="host@email.com",
            ),
            name="Test Room",
            description="Test Description"
        )
        
        self.report1 = Report.objects.create(
            user=self.user,
            room=self.room,
            reason="SPAM",
            body="First report"
        )
        self.report2 = Report.objects.create(
            user=self.user, 
            room=self.room,
            reason="HARASSMENT",
            body="Second report",
            status="RESOLVED"
        )

    def test_my_reports(self):
        self.client.authenticate(self.user)
        query = """
            query {
                myReports {
                    reason
                    body
                    status
                }
            }
        """
        result: ExecutionResult = self.client.execute(query)
        self.assertIsNone(result.errors)
        self.assertEqual(len(result.data["myReports"]), 2)

    def test_report_detail(self):
        self.client.authenticate(self.user)
        query = """
            query GetReport($reportId: UUID!) {
                report(reportId: $reportId) {
                    reason
                    body
                }
            }
        """
        variables = {"reportId": str(self.report1.id)}
        result: ExecutionResult = self.client.execute(query, variables)
        self.assertIsNone(result.errors)
        self.assertEqual(result.data["report"]["reason"], "SPAM")

    def test_all_reports_as_moderator(self):
        self.client.authenticate(self.moderator)
        query = """
            query {
                allReports {
                    reason
                    status
                }
            }
        """
        result: ExecutionResult = self.client.execute(query)
        self.assertIsNone(result.errors)
        self.assertEqual(len(result.data["allReports"]), 2)

    def test_report_count_as_moderator(self):
        self.client.authenticate(self.moderator)
        query = """
            query {
                reportCount
            }
        """
        result: ExecutionResult = self.client.execute(query)
        self.assertIsNone(result.errors)
        self.assertEqual(result.data["reportCount"], 2)

    def test_report_count_with_filter(self):
        self.client.authenticate(self.moderator)
        query = """
            query ReportCount($status: String) {
                reportCount(status: $status)
            }
        """
        variables = {"status": "PENDING"}
        result: ExecutionResult = self.client.execute(query, variables)
        self.assertIsNone(result.errors)
        self.assertEqual(result.data["reportCount"], 1)