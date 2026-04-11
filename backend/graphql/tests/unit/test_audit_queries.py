import pghistory
import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from graphql_sync_dataloaders import DeferredExecutionContext
from graphql_jwt.testcases import JSONWebTokenClient, JSONWebTokenTestCase

from backend.access.models import Role
from backend.graphql.context.registry import GQLDataLoaderRegistry
from backend.invite.models import Invite
from backend.room.models import Room
from backend.room.choices import VisibilityChoices
from backend.invite.choices import InviteStatusChoices

pytestmark = pytest.mark.unit

User = get_user_model()


class DataLoaderClient(JSONWebTokenClient):
    """
    Extends JSONWebTokenClient with two things the test client lacks:

    1. request.loaders — attached in request() which is the method
       JSONWebTokenClient.execute() ultimately calls to build its context,
       mirroring what GQLDataLoaderMiddleware does in production.

    2. DeferredExecutionContext — wired into the schema execution so
       SyncDataLoader batching is honoured, exactly as in the production
       GraphQLView. Without this, .load() still works but each call hits
       the DB individually (no batching).
    """

    def request(self, **request):
        wsgi_request = super().request(**request)
        wsgi_request.loaders = GQLDataLoaderRegistry()
        return wsgi_request

    def execute(self, query, variables=None, **extra):
        extra.update(self._credentials)
        context = self.post("/", **extra)
        return self._schema.execute(
            query,
            context_value=context,
            variable_values=variables,
            execution_context_class=DeferredExecutionContext,
            middleware=[m() for m in self._middleware],
        )


class AuditQueryTests(JSONWebTokenTestCase):
    client_class = DataLoaderClient

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

        with pghistory.context(user=self.user.id):
            room = Room.objects.create(
                host=self.user,
                name="Audit Room",
                description="Initial",
                visibility=VisibilityChoices.PUBLIC,
            )
            room.name = "Audit Room Updated"
            room.visibility = VisibilityChoices.PRIVATE
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

        response = self.client.execute(query)
        self.assertIsNone(response.errors)
        data = response.data["roomAudits"]["edges"]
        self.assertGreater(len(data), 0)

        latest = data[0]["node"]
        self.assertEqual(latest["name"], "Audit Room Updated")
        self.assertEqual(latest["visibility"], VisibilityChoices.PRIVATE)
        self.assertEqual(latest["actor"]["username"], self.user.username)
        self.assertEqual(str(latest["pghObjId"]), str(room.id))

        response = self.client.execute(query, variables={"name": "Updated"})
        self.assertIsNone(response.errors)
        self.assertGreater(len(response.data["roomAudits"]["edges"]), 0)

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

        with pghistory.context(user=self.superuser.id):
            self.user.is_active = False
            self.user.save()

        query = """
            query GetUserAudits($actorUsername: String) {
                userAudits(actorUsername: $actorUsername) {
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
            query,
            variables={"actorUsername": self.superuser.username},
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

        with pghistory.context(user=self.user.id):
            invite = Invite.objects.create(
                room=room,
                inviter=self.user,
                invitee=self.other_user,
                role=role,
                expires_at=timezone.now() + timezone.timedelta(days=1),
            )
            invite.status = InviteStatusChoices.ACCEPTED
            invite.save()

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

        response = self.client.execute(
            query, variables={"dateFrom": yesterday, "dateTo": tomorrow}
        )
        self.assertIsNone(response.errors)
        self.assertGreater(len(response.data["userAudits"]["edges"]), 0)

        future_start = (now + timezone.timedelta(days=2)).date().isoformat()
        future_end = (now + timezone.timedelta(days=3)).date().isoformat()

        response = self.client.execute(
            query, variables={"dateFrom": future_start, "dateTo": future_end}
        )
        self.assertIsNone(response.errors)
        self.assertEqual(len(response.data["userAudits"]["edges"]), 0)
