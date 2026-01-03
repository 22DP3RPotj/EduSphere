import pytest

pytestmark = [pytest.mark.unit, pytest.mark.services]

from backend.access.enums import RoleCode
from backend.access.models import Participant
from backend.access.services import ParticipantService, RoleService
from backend.core.exceptions import ConflictException, FormValidationException, PermissionException, ValidationException
from backend.room.models import Room
from backend.tests.service_base import ServiceTestBase


class ParticipantServiceTest(ServiceTestBase):
    """Test ParticipantService methods."""

    def test_get_participant_success(self):
        self._add_member(self.member, self.member_role)

        participant = ParticipantService.get_participant(self.member, self.room)

        self.assertIsNotNone(participant)
        self.assertEqual(participant.user, self.member)
        self.assertEqual(participant.room, self.room)

    def test_get_participant_not_found(self):
        participant = ParticipantService.get_participant(self.other_user, self.room)
        self.assertIsNone(participant)

    def test_add_participant_success(self):
        participant = ParticipantService.add_participant(room=self.room, user=self.other_user, role=self.member_role)

        self.assertEqual(participant.user, self.other_user)
        self.assertEqual(participant.room, self.room)
        self.assertEqual(participant.role, self.member_role)

    def test_add_participant_already_exists(self):
        self._add_member(self.member, self.member_role)

        with self.assertRaises(ConflictException):
            ParticipantService.add_participant(room=self.room, user=self.member, role=self.member_role)

    def test_add_participant_role_wrong_room(self):
        other_room = Room.objects.create(
            host=self.owner,
            name="Other Room",
            description="",
            visibility=Room.Visibility.PUBLIC,
        )
        RoleService.create_default_roles(other_room)
        other_role = other_room.roles.first()

        with self.assertRaises((ValidationException, FormValidationException)):
            ParticipantService.add_participant(room=self.room, user=self.other_user, role=other_role)

    def test_change_participant_role_success(self):
        participant = self._add_member(self.other_user, self.member_role)

        moderator_role = (
            self.room.roles.filter(priority__lt=100).exclude(name=RoleCode.OWNER.label).first()
        )

        result = ParticipantService.change_participant_role(
            user=self.owner,
            participant=participant,
            new_role=moderator_role,
        )

        self.assertEqual(result.role, moderator_role)

    def test_change_participant_role_no_permission(self):
        participant = self._add_member(self.other_user, self.member_role)
        self._add_member(self.member, self.member_role)

        with self.assertRaises(PermissionException):
            ParticipantService.change_participant_role(
                user=self.member,
                participant=participant,
                new_role=self.member_role,
            )

    def test_change_participant_role_wrong_room(self):
        participant = self._add_member(self.other_user, self.member_role)

        other_room = Room.objects.create(
            host=self.owner,
            name="Other Room",
            description="",
            visibility=Room.Visibility.PUBLIC,
        )
        RoleService.create_default_roles(other_room)
        other_role = other_room.roles.first()

        with self.assertRaises((ValidationException, FormValidationException)):
            ParticipantService.change_participant_role(
                user=self.owner,
                participant=participant,
                new_role=other_role,
            )

    def test_remove_participant_self(self):
        self._add_member(self.member, self.member_role)
        participant = Participant.objects.get(user=self.member, room=self.room)

        result = ParticipantService.remove_participant(self.member, participant)

        self.assertTrue(result)
        self.assertFalse(Participant.objects.filter(id=participant.id).exists())

    def test_remove_participant_with_permission(self):
        participant = self._add_member(self.other_user, self.member_role)

        result = ParticipantService.remove_participant(self.owner, participant)

        self.assertTrue(result)
        self.assertFalse(Participant.objects.filter(id=participant.id).exists())

    def test_remove_participant_no_permission(self):
        self._add_member(self.member, self.member_role)
        participant = self._add_member(self.other_user, self.member_role)

        with self.assertRaises(PermissionException):
            ParticipantService.remove_participant(self.member, participant)

    def test_get_user_rooms(self):
        self._add_member(self.member, self.member_role)

        other_room = Room.objects.create(
            host=self.owner,
            name="Other Room",
            description="",
            visibility=Room.Visibility.PUBLIC,
        )
        RoleService.create_default_roles(other_room)
        other_role = other_room.roles.get(name=RoleCode.MEMBER.label)
        Participant.objects.create(user=self.member, room=other_room, role=other_role)

        rooms = ParticipantService.get_user_rooms(self.member)

        self.assertEqual(rooms.count(), 2)
        self.assertIn(self.room, rooms)
        self.assertIn(other_room, rooms)
