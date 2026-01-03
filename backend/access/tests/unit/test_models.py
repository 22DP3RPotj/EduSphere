from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase, tag

from backend.access.enums import PermissionCode
from backend.access.models import Participant, Permission, Role
from backend.room.models import Room

User = get_user_model()


@tag("unit")
class PermissionModelTest(TestCase):
    def test_permission_creation(self):
        permission, _created = Permission.objects.get_or_create(
            code=PermissionCode.ROOM_DELETE,
            defaults={"description": "Delete room"},
        )
        self.assertEqual(permission.code, PermissionCode.ROOM_DELETE)

    def test_permission_str(self):
        permission, _created = Permission.objects.get_or_create(
            code=PermissionCode.ROOM_UPDATE,
            defaults={"description": "Update room"},
        )
        self.assertEqual(str(permission), PermissionCode.ROOM_UPDATE)


@tag("unit")
class RoleModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            name="Host",
            username="host",
            email="host@email.com",
        )
        self.room = Room.objects.create(
            host=self.user,
            name="Test Room",
            description="",
            visibility=Room.Visibility.PUBLIC,
        )

    def test_role_creation(self):
        role = Role.objects.create(
            room=self.room,
            name="Admin",
            description="Administrator role",
            priority=100,
        )
        self.assertEqual(role.name, "Admin")
        self.assertEqual(role.priority, 100)

    def test_role_unique_constraint(self):
        Role.objects.create(
            room=self.room,
            name="Admin",
            description="Admin role",
            priority=100,
        )
        with self.assertRaises(Exception):
            Role.objects.create(
                room=self.room,
                name="Admin",
                description="Another admin",
                priority=50,
            )

    def test_role_str(self):
        role = Role.objects.create(
            room=self.room,
            name="Moderator",
            description="Moderator role",
            priority=50,
        )
        self.assertEqual(str(role), "Moderator")


@tag("unit")
class ParticipantModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            name="Host",
            username="host",
            email="host@email.com",
        )
        self.participant_user = User.objects.create_user(
            name="Participant",
            username="participant",
            email="participant@email.com",
        )
        self.room = Room.objects.create(
            host=self.user,
            name="Test Room",
            description="",
            visibility=Room.Visibility.PUBLIC,
        )
        self.role = Role.objects.create(
            room=self.room,
            name="Member",
            description="Member",
            priority=0,
        )

    def test_participant_creation(self):
        participant = Participant.objects.create(
            user=self.participant_user,
            room=self.room,
            role=self.role,
        )
        self.assertEqual(participant.user, self.participant_user)
        self.assertEqual(participant.room, self.room)

    def test_participant_unique_constraint(self):
        Participant.objects.create(
            user=self.participant_user,
            room=self.room,
            role=self.role,
        )
        with self.assertRaises(Exception):
            Participant.objects.create(
                user=self.participant_user,
                room=self.room,
                role=self.role,
            )

    def test_participant_str(self):
        participant = Participant.objects.create(
            user=self.participant_user,
            room=self.room,
            role=self.role,
        )
        self.assertEqual(str(participant), "participant in Test Room")

    def test_participant_role_validation(self):
        other_room = Room.objects.create(
            host=self.user,
            name="Other Room",
            description="",
            visibility=Room.Visibility.PUBLIC,
        )
        other_role = Role.objects.create(
            room=other_room,
            name="Other Role",
            description="",
            priority=0,
        )
        participant = Participant(
            user=self.participant_user,
            room=self.room,
            role=other_role,
        )
        with self.assertRaises(ValidationError):
            participant.full_clean()
