from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone

import pytest

pytestmark = [pytest.mark.integration, pytest.mark.services]

from backend.access.enums import PermissionCode, RoleCode
from backend.access.models import Participant
from backend.access.services import ParticipantService, RoleService
from backend.invite.services import InviteService
from backend.messaging.models import Message
from backend.messaging.services import MessageService
from backend.room.models import Room
from backend.room.services import RoomService
from backend.tests.service_base import ServiceTestBase

User = get_user_model()


class IntegrationTests(ServiceTestBase):
    """Cross-service integration tests."""

    def test_full_room_workflow_with_role_management(self):
        room = RoomService.create_room(
            user=self.owner,
            name="Complete Workflow Room",
            description="Test workflow",
            visibility=Room.Visibility.PRIVATE,
            topic_names=["test"],
        )

        member_role = room.roles.get(name=RoleCode.MEMBER.label)

        user1 = User.objects.create_user(
            name="Workflow User 1",
            username="workflow_user1",
            email="workflow1@test.com",
            password="testpass123",
        )
        user2 = User.objects.create_user(
            name="Workflow User 2",
            username="workflow_user2",
            email="workflow2@test.com",
            password="testpass123",
        )

        ParticipantService.add_participant(room, user1, member_role)
        ParticipantService.add_participant(room, user2, member_role)

        self.assertEqual(room.participants.count(), 3)

        invite = InviteService.send_invite(
            inviter=self.owner,
            room=room,
            invitee=self.other_user,
            role=member_role,
            expires_at=timezone.now() + timedelta(days=7),
        )

        InviteService.accept_invite(self.other_user, invite)
        self.assertEqual(room.participants.count(), 4)

        message = MessageService.create_message(user=self.other_user, room=room, body="Hello from new participant")
        self.assertIsNotNone(message.id)

        updated = MessageService.update_message(user=self.other_user, message=message, body="Updated message")
        self.assertTrue(updated.is_edited)

    def test_permission_check_with_role_changes(self):
        self._add_member(self.member, self.member_role)

        has_perm = RoleService.has_permission(self.member, self.room, PermissionCode.ROOM_UPDATE)
        self.assertFalse(has_perm)

        has_perm = RoleService.has_permission(self.owner, self.room, PermissionCode.ROOM_UPDATE)
        self.assertTrue(has_perm)

    def test_cascading_delete_with_messages(self):
        self._add_member(self.member, self.member_role)

        MessageService.create_message(user=self.member, room=self.room, body="Message 1")
        MessageService.create_message(user=self.member, room=self.room, body="Message 2")

        self.assertEqual(Message.objects.filter(user=self.member).count(), 2)

        participant = Participant.objects.get(user=self.member, room=self.room)
        ParticipantService.remove_participant(self.owner, participant)

        self.assertFalse(Participant.objects.filter(user=self.member, room=self.room).exists())

    def test_invite_to_private_room(self):
        private_room = RoomService.create_room(
            user=self.owner,
            name="Private Room",
            description="",
            visibility=self.room.Visibility.PRIVATE,
            topic_names=[],
        )

        member_role = private_room.roles.get(name=RoleCode.MEMBER.label)

        invite = InviteService.send_invite(
            inviter=self.owner,
            room=private_room,
            invitee=self.member,
            role=member_role,
            expires_at=timezone.now() + timedelta(days=7),
        )

        self.assertIsNotNone(invite.id)
