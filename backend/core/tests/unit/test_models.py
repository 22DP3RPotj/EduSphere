from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase, tag
from django.core.exceptions import ValidationError
from django.utils import timezone

from backend.messaging.models import Message
from backend.invite.models import Invite
from backend.moderation.models import Report
from backend.room.models import Room, Topic
from backend.access.models import Permission, Role, Participant
from backend.access.enums import PermissionCode

User = get_user_model()


@tag("unit")
class UserModelTest(TestCase):
    def test_user_creation(self):
        user = User.objects.create_user(
            name="Test User",
            username="testuser",
            email="test@email.com",
            password="testpass123"
        )
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "test@email.com")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)

    def test_user_slug_conversion(self):
        user = User.objects.create_user(
            name="Test User",
            username="Test User",
            email="test@email.com",
        )
        self.assertEqual(user.username, "test-user")

    def test_user_str(self):
        user = User.objects.create_user(
            name="Test User",
            username="testuser",
            email="test@email.com",
        )
        self.assertEqual(str(user), "testuser")


@tag("unit")
class TopicModelTest(TestCase):
    def test_topic_creation(self):
        topic = Topic.objects.create(name="Programming")
        self.assertEqual(topic.name, "Programming")

    def test_topic_str(self):
        topic = Topic.objects.create(name="Music")
        self.assertEqual(str(topic), "Music")

    def test_topic_invalid_name(self):
        with self.assertRaises(ValidationError):
            topic = Topic(name="Music123")
            topic.full_clean()


@tag("unit")
class RoomModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            name="Host",
            username="host",
            email="host@email.com"
        )

    def test_room_creation(self):
        room = Room.objects.create(
            host=self.user,
            name="Test Room",
            description="Test Description",
            visibility=Room.Visibility.PUBLIC
        )
        self.assertEqual(room.name, "Test Room")
        self.assertEqual(room.host, self.user)
        self.assertEqual(room.visibility, Room.Visibility.PUBLIC)

    def test_room_slug_generation(self):
        room = Room.objects.create(
            host=self.user,
            name="Test Room",
            description="",
            visibility=Room.Visibility.PUBLIC
        )
        self.assertEqual(room.slug, "test-room")

    def test_room_unique_constraint(self):
        Room.objects.create(
            host=self.user,
            name="Duplicate Room",
            description="",
            visibility=Room.Visibility.PUBLIC
        )
        with self.assertRaises(Exception):
            Room.objects.create(
                host=self.user,
                name="Duplicate Room",
                description="",
                visibility=Room.Visibility.PUBLIC
            )

    def test_room_str(self):
        room = Room.objects.create(
            host=self.user,
            name="Test Room",
            description="",
            visibility=Room.Visibility.PUBLIC
        )
        self.assertEqual(str(room), "Test Room")


@tag("unit")
class PermissionModelTest(TestCase):
    def test_permission_creation(self):
        permission, created = Permission.objects.get_or_create(
            code=PermissionCode.ROOM_DELETE,
            defaults={"description": "Delete room"}
        )
        self.assertEqual(permission.code, PermissionCode.ROOM_DELETE)

    def test_permission_str(self):
        permission, created = Permission.objects.get_or_create(
            code=PermissionCode.ROOM_UPDATE,
            defaults={"description": "Update room"}
        )
        self.assertEqual(str(permission), PermissionCode.ROOM_UPDATE)


@tag("unit")
class RoleModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            name="Host",
            username="host",
            email="host@email.com"
        )
        self.room = Room.objects.create(
            host=self.user,
            name="Test Room",
            description="",
            visibility=Room.Visibility.PUBLIC
        )

    def test_role_creation(self):
        role = Role.objects.create(
            room=self.room,
            name="Admin",
            description="Administrator role",
            priority=100
        )
        self.assertEqual(role.name, "Admin")
        self.assertEqual(role.priority, 100)

    def test_role_unique_constraint(self):
        Role.objects.create(
            room=self.room,
            name="Admin",
            description="Admin role",
            priority=100
        )
        with self.assertRaises(Exception):
            Role.objects.create(
                room=self.room,
                name="Admin",
                description="Another admin",
                priority=50
            )

    def test_role_str(self):
        role = Role.objects.create(
            room=self.room,
            name="Moderator",
            description="Moderator role",
            priority=50
        )
        self.assertEqual(str(role), "Moderator")


@tag("unit")
class ParticipantModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            name="Host",
            username="host",
            email="host@email.com"
        )
        self.participant_user = User.objects.create_user(
            name="Participant",
            username="participant",
            email="participant@email.com"
        )
        self.room = Room.objects.create(
            host=self.user,
            name="Test Room",
            description="",
            visibility=Room.Visibility.PUBLIC
        )
        self.role = Role.objects.create(
            room=self.room,
            name="Member",
            description="Member",
            priority=0
        )

    def test_participant_creation(self):
        participant = Participant.objects.create(
            user=self.participant_user,
            room=self.room,
            role=self.role
        )
        self.assertEqual(participant.user, self.participant_user)
        self.assertEqual(participant.room, self.room)

    def test_participant_unique_constraint(self):
        Participant.objects.create(
            user=self.participant_user,
            room=self.room,
            role=self.role
        )
        with self.assertRaises(Exception):
            Participant.objects.create(
                user=self.participant_user,
                room=self.room,
                role=self.role
            )

    def test_participant_str(self):
        participant = Participant.objects.create(
            user=self.participant_user,
            room=self.room,
            role=self.role
        )
        self.assertEqual(str(participant), "participant in Test Room")

    def test_participant_role_validation(self):
        other_room = Room.objects.create(
            host=self.user,
            name="Other Room",
            description="",
            visibility=Room.Visibility.PUBLIC
        )
        other_role = Role.objects.create(
            room=other_room,
            name="Other Role",
            description="",
            priority=0
        )
        participant = Participant(
            user=self.participant_user,
            room=self.room,
            role=other_role
        )
        with self.assertRaises(ValidationError):
            participant.full_clean()


@tag("unit")
class MessageModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            name="User",
            username="user",
            email="user@email.com"
        )
        self.room = Room.objects.create(
            host=self.user,
            name="Test Room",
            description="",
            visibility=Room.Visibility.PUBLIC
        )

    def test_message_creation(self):
        message = Message.objects.create(
            user=self.user,
            room=self.room,
            body="Hello world!"
        )
        self.assertEqual(message.body, "Hello world!")
        self.assertFalse(message.is_edited)

    def test_message_str(self):
        message = Message.objects.create(
            user=self.user,
            room=self.room,
            body="A" * 100
        )
        self.assertEqual(str(message), "A" * 50 + "...")

    def test_message_str_short(self):
        message = Message.objects.create(
            user=self.user,
            room=self.room,
            body="Short"
        )
        self.assertEqual(str(message), "Short")

    def test_message_parent_validation(self):
        other_room = Room.objects.create(
            host=self.user,
            name="Other Room",
            description="",
            visibility=Room.Visibility.PUBLIC
        )
        parent_message = Message.objects.create(
            user=self.user,
            room=other_room,
            body="Parent"
        )
        child_message = Message(
            user=self.user,
            room=self.room,
            body="Child",
            parent=parent_message
        )
        with self.assertRaises(ValidationError):
            child_message.full_clean()


@tag("unit")
class ReportModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            name="User",
            username="user",
            email="user@email.com"
        )
        self.moderator = User.objects.create_user(
            name="Moderator",
            username="moderator",
            email="moderator@email.com",
            is_staff=True,
            is_superuser=True
        )
        self.room = Room.objects.create(
            host=self.user,
            name="Test Room",
            description="",
            visibility=Room.Visibility.PUBLIC
        )

    def test_report_creation(self):
        report = Report.objects.create(
            user=self.user,
            room=self.room,
            reason=Report.ReportReason.SPAM,
            body="This is spam",
            status=Report.ReportStatus.PENDING
        )
        self.assertEqual(report.status, Report.ReportStatus.PENDING)
        self.assertTrue(report.is_active_report)

    def test_report_active_reports(self):
        Report.objects.create(
            user=self.user,
            room=self.room,
            reason=Report.ReportReason.SPAM,
            body="Spam",
            status=Report.ReportStatus.PENDING
        )
        Report.objects.create(
            user=self.user,
            room=self.room,
            reason=Report.ReportReason.HARASSMENT,
            body="Harassment",
            status=Report.ReportStatus.RESOLVED
        )
        active = Report.active_reports()
        self.assertEqual(active.count(), 1)

    def test_report_str(self):
        report = Report.objects.create(
            user=self.user,
            room=self.room,
            reason=Report.ReportReason.SPAM,
            body="Spam",
            status=Report.ReportStatus.PENDING
        )
        self.assertEqual(str(report), f"Report by user on Test Room")


@tag("unit")
class InviteModelTest(TestCase):
    def setUp(self):
        self.inviter = User.objects.create_user(
            name="Inviter",
            username="inviter",
            email="inviter@email.com"
        )
        self.invitee = User.objects.create_user(
            name="Invitee",
            username="invitee",
            email="invitee@email.com"
        )
        self.room = Room.objects.create(
            host=self.inviter,
            name="Test Room",
            description="",
            visibility=Room.Visibility.PUBLIC
        )
        self.role = Role.objects.create(
            room=self.room,
            name="Member",
            description="Member",
            priority=0
        )

    def test_invite_creation(self):
        invite = Invite.objects.create(
            room=self.room,
            inviter=self.inviter,
            invitee=self.invitee,
            role=self.role,
            expires_at=timezone.now() + timedelta(days=7)
        )
        self.assertEqual(invite.status, Invite.InviteStatus.PENDING)

    def test_invite_is_expired(self):
        invite = Invite.objects.create(
            room=self.room,
            inviter=self.inviter,
            invitee=self.invitee,
            role=self.role,
            expires_at=timezone.now() - timedelta(hours=1)
        )
        self.assertTrue(invite.is_expired)

    def test_invite_not_expired(self):
        invite = Invite.objects.create(
            room=self.room,
            inviter=self.inviter,
            invitee=self.invitee,
            role=self.role,
            expires_at=timezone.now() + timedelta(days=7)
        )
        self.assertFalse(invite.is_expired)

    def test_invite_unique_constraint(self):
        Invite.objects.create(
            room=self.room,
            inviter=self.inviter,
            invitee=self.invitee,
            role=self.role,
            expires_at=timezone.now() + timedelta(days=7)
        )
        with self.assertRaises(Exception):
            Invite.objects.create(
                room=self.room,
                inviter=self.inviter,
                invitee=self.invitee,
                role=self.role,
                expires_at=timezone.now() + timedelta(days=7)
            )

    def test_invite_str(self):
        invite = Invite.objects.create(
            room=self.room,
            inviter=self.inviter,
            invitee=self.invitee,
            role=self.role,
            expires_at=timezone.now() + timedelta(days=7)
        )
        self.assertEqual(str(invite), "Invite of invitee to Test Room by inviter")
