import pytest

pytestmark = [pytest.mark.unit, pytest.mark.services]

from backend.access.enums import RoleCode
from backend.access.models import Participant
from backend.core.exceptions import FormValidationException, PermissionException
from backend.room.models import Room
from backend.room.services import RoomService
from backend.core.tests.service_base import ServiceTestBase


class RoomServiceTest(ServiceTestBase):
    """Test RoomService methods."""

    def test_can_view_participant(self):
        self._add_member(self.member, self.member_role)
        self.assertTrue(RoomService.can_view(self.member, self.room))

    def test_can_view_public_room(self):
        self.assertTrue(RoomService.can_view(self.other_user, self.room))

    def test_cannot_view_private_room(self):
        private_room = Room.objects.create(
            host=self.owner,
            name="Private Room",
            description="",
            visibility=Room.Visibility.PRIVATE,
        )
        self.assertFalse(RoomService.can_view(self.other_user, private_room))

    def test_create_room_success(self):
        room = RoomService.create_room(
            user=self.other_user,
            name="New Room",
            description="A new test room",
            visibility=Room.Visibility.PUBLIC,
            topic_names=["Programming", "Python"],
        )

        self.assertEqual(room.name, "New Room")
        self.assertEqual(room.host, self.other_user)
        self.assertEqual(room.visibility, Room.Visibility.PUBLIC)
        self.assertEqual(room.topics.count(), 2)

        owner_participant = Participant.objects.get(user=self.other_user, room=room)
        self.assertEqual(owner_participant.role.name, RoleCode.OWNER.label)

    def test_create_room_invalid_data(self):
        with self.assertRaises(FormValidationException):
            RoomService.create_room(
                user=self.other_user,
                name="",
                description="",
                visibility=Room.Visibility.PUBLIC,
                topic_names=[],
            )

    def test_update_room_success(self):
        updated = RoomService.update_room(
            user=self.owner,
            room=self.room,
            name="Updated Room Name",
            description="Updated description",
            visibility=Room.Visibility.PRIVATE,
            topic_names=["NewTopic"],
        )

        self.assertEqual(updated.name, "Updated Room Name")
        self.assertEqual(updated.description, "Updated description")
        self.assertEqual(updated.visibility, Room.Visibility.PRIVATE)
        self.assertEqual(updated.topics.count(), 1)

    def test_update_room_no_permission(self):
        with self.assertRaises(PermissionException):
            RoomService.update_room(
                user=self.other_user, room=self.room, name="Hacked Room"
            )

    def test_delete_room_success(self):
        result = RoomService.delete_room(self.owner, self.room)

        self.assertTrue(result)
        self.assertFalse(Room.objects.filter(id=self.room.id).exists())

    def test_delete_room_no_permission(self):
        with self.assertRaises(PermissionException):
            RoomService.delete_room(self.other_user, self.room)
