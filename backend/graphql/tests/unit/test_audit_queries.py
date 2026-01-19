import pghistory
import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from graphql_jwt.testcases import JSONWebTokenTestCase

from backend.access.models import Role
from backend.invite.models import Invite
from backend.room.models import Room
from backend.room.choices import RoomVisibility
from backend.invite.choices import InviteStatus

pytestmark = pytest.mark.unit

User = get_user_model()


class AuditQueryTests(JSONWebTokenTestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username="superuser",
            email="super@test.com",
            password="password",
            name="Super User",
        )
        self.user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="password",
            name="Test User",
        )
        self.other_user = User.objects.create_user(
            username="otheruser",
            email="other@test.com",
            password="password",
            name="Other User",
        )

    def test_audit_permissions(self):
        """Verify that non-superusers cannot access audit logs."""
        self.client.authenticate(self.user)

        queries = [
            """query { userAudits { edges { node { pghId } } } }""",
            """query { roomAudits { edges { node { pghId } } } }""",
            """query { inviteAudits { edges { node { pghId } } } }""",
        ]

        for query in queries:
            response = self.client.execute(query)
            self.assertIsNotNone(response.errors)
            self.assertIn("permission", str(response.errors[0]).lower())

    def test_room_audits(self):
        """Test room audit logging, actor resolution, and filtering."""
        self.client.authenticate(self.superuser)

        # Create room and update it to generate history
        with pghistory.context(user=self.user.id):
            room = Room.objects.create(
                host=self.user,
                name="Audit Room",
                description="Initial",
                visibility=RoomVisibility.PUBLIC,
            )
            # Update to trigger history
            room.name = "Audit Room Updated"
            room.visibility = RoomVisibility.PRIVATE
            room.save()

        query = """
            query GetRoomAudits($name: String, $targetId: UUID) {
                roomAudits(name: $name, targetId: $targetId) {
                    edges {
                        node {
                            pghObjId
                            pghLabel
                            actor {
                                username
                            }
                            name
                            visibility
                        }
                    }
                }
            }
        """

        # Query all
        response = self.client.execute(query)
        self.assertIsNone(response.errors)
        data = response.data["roomAudits"]["edges"]

        # Depending on pghistory config, we expect at least the update event
        self.assertGreater(len(data), 0)

        # Verify the latest update
        latest = data[-1]["node"]
        self.assertEqual(latest["name"], "Audit Room Updated")
        self.assertEqual(latest["visibility"], RoomVisibility.PRIVATE)
        self.assertEqual(latest["actor"]["username"], self.user.username)
        self.assertEqual(str(latest["pghObjId"]), str(room.id))

        # Test Filter by name
        response = self.client.execute(query, variables={"name": "Updated"})
        self.assertIsNone(response.errors)
        self.assertGreater(len(response.data["roomAudits"]["edges"]), 0)

        # Test Filter by targetId
        response = self.client.execute(query, variables={"targetId": str(room.id)})
        self.assertIsNone(response.errors)
        self.assertGreater(len(response.data["roomAudits"]["edges"]), 0)
        self.assertEqual(
            str(response.data["roomAudits"]["edges"][0]["node"]["pghObjId"]),
            str(room.id),
        )

        response = self.client.execute(query, variables={"name": "NonExistent"})
        self.assertIsNone(response.errors)
        self.assertEqual(len(response.data["roomAudits"]["edges"]), 0)

    def test_user_audits(self):
        """Test user audit logging and filters."""
        self.client.authenticate(self.superuser)

        # Update user to generate history
        with pghistory.context(user=self.superuser.id):
            self.user.is_active = False
            self.user.save()

        query = """
            query GetUserAudits($username: String) {
                userAudits(username: $username) {
                    edges {
                        node {
                            pghObjId
                            actor { username }
                            isStaff
                            isActive
                        }
                    }
                }
            }
        """

        response = self.client.execute(
            query, variables={"username": self.user.username}
        )
        self.assertIsNone(response.errors)
        data = response.data["userAudits"]["edges"]
        self.assertGreater(len(data), 0)

        latest = data[-1]["node"]
        self.assertEqual(latest["isActive"], False)
        self.assertEqual(latest["actor"]["username"], self.superuser.username)
        self.assertEqual(str(latest["pghObjId"]), str(self.user.id))

    def test_invite_audits(self):
        """Test invite audit logging for status changes."""
        self.client.authenticate(self.superuser)

        room = Room.objects.create(host=self.user, name="Invite Room")
        role = Role.objects.create(room=room, name="Guest", priority=1)

        # Create invite
        with pghistory.context(user=self.user.id):
            invite = Invite.objects.create(
                room=room,
                inviter=self.user,
                invitee=self.other_user,
                role=role,
                expires_at=timezone.now() + timezone.timedelta(days=1),
            )

            # Update status
            invite.status = InviteStatus.ACCEPTED
            invite.save()

        # Use literal enum value to avoid type issues with variables
        query = """
            query GetInviteAudits {
                inviteAudits(status: ACCEPTED) {
                    edges {
                        node {
                            pghObjId
                            status
                            role { id }
                            actor { username }
                        }
                    }
                }
            }
        """

        response = self.client.execute(query)
        self.assertIsNone(response.errors)
        data = response.data["inviteAudits"]["edges"]
        self.assertGreater(len(data), 0)

        latest = data[0]["node"]
        self.assertEqual(latest["status"], "ACCEPTED")
        self.assertEqual(latest["actor"]["username"], self.user.username)
        self.assertEqual(str(latest["pghObjId"]), str(invite.id))

    def test_date_range_filter(self):
        """Test common date filtering across audit logs."""
        self.client.authenticate(self.superuser)

        # Generate an event "now"
        with pghistory.context(user=self.user.id):
            self.user.name = "Time Test"
            self.user.save()

        now = timezone.now()
        yesterday = (now - timezone.timedelta(days=1)).date().isoformat()
        tomorrow = (now + timezone.timedelta(days=1)).date().isoformat()

        query = """
            query DateFilter($dateFrom: Date, $dateTo: Date) {
                userAudits(dateFrom: $dateFrom, dateTo: $dateTo) {
                    edges {
                        node {
                            pghCreatedAt
                        }
                    }
                }
            }
        """

        # Test valid range
        response = self.client.execute(
            query, variables={"dateFrom": yesterday, "dateTo": tomorrow}
        )
        self.assertIsNone(response.errors)
        self.assertGreater(len(response.data["userAudits"]["edges"]), 0)

        # Test future range (should be empty if we haven't created future events)
        future_start = (now + timezone.timedelta(days=2)).date().isoformat()
        future_end = (now + timezone.timedelta(days=3)).date().isoformat()

        response = self.client.execute(
            query, variables={"dateFrom": future_start, "dateTo": future_end}
        )
        self.assertIsNone(response.errors)
        self.assertEqual(len(response.data["userAudits"]["edges"]), 0)
