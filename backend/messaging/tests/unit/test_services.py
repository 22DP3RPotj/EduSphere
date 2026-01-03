import pytest

pytestmark = [pytest.mark.unit, pytest.mark.services]

from backend.core.exceptions import FormValidationException, PermissionException, ValidationException
from backend.messaging.models import Message
from backend.messaging.services import MessageService
from backend.tests.service_base import ServiceTestBase


class MessageServiceTest(ServiceTestBase):
    """Test MessageService methods."""

    def test_create_message_success(self):
        self._add_member(self.member, self.member_role)

        message = MessageService.create_message(user=self.member, room=self.room, body="Test message content")

        self.assertIsNotNone(message)
        self.assertEqual(message.user, self.member)
        self.assertEqual(message.room, self.room)
        self.assertEqual(message.body, "Test message content")
        self.assertFalse(message.is_edited)

    def test_create_message_not_participant(self):
        with self.assertRaises(PermissionException):
            MessageService.create_message(user=self.other_user, room=self.room, body="Test message")

    def test_create_message_invalid_data(self):
        self._add_member(self.member, self.member_role)

        with self.assertRaises((ValidationException, FormValidationException)):
            MessageService.create_message(user=self.member, room=self.room, body="")

    def test_update_message_success(self):
        self._add_member(self.member, self.member_role)

        message = MessageService.create_message(user=self.member, room=self.room, body="Original content")

        updated = MessageService.update_message(user=self.member, message=message, body="Updated content")

        self.assertEqual(updated.body, "Updated content")
        self.assertTrue(updated.is_edited)

    def test_update_message_not_author(self):
        self._add_member(self.member, self.member_role)
        self._add_member(self.other_user, self.member_role)

        message = MessageService.create_message(user=self.member, room=self.room, body="Test message")

        with self.assertRaises(PermissionException):
            MessageService.update_message(user=self.other_user, message=message, body="Hacked message")

    def test_update_message_invalid_data(self):
        self._add_member(self.member, self.member_role)

        message = MessageService.create_message(user=self.member, room=self.room, body="Test message")

        with self.assertRaises(FormValidationException):
            MessageService.update_message(user=self.member, message=message, body="")

    def test_delete_message_author(self):
        self._add_member(self.member, self.member_role)

        message = MessageService.create_message(user=self.member, room=self.room, body="Test message")

        result = MessageService.delete_message(self.member, message)

        self.assertTrue(result)
        self.assertFalse(Message.objects.filter(id=message.id).exists())

    def test_delete_message_not_author_no_permission(self):
        self._add_member(self.member, self.member_role)
        self._add_member(self.other_user, self.member_role)

        message = MessageService.create_message(user=self.member, room=self.room, body="Test message")

        with self.assertRaises(PermissionException):
            MessageService.delete_message(self.other_user, message)

    def test_delete_message_with_permission(self):
        self._add_member(self.member, self.member_role)

        message = MessageService.create_message(user=self.member, room=self.room, body="Test message")

        result = MessageService.delete_message(self.owner, message)
        self.assertTrue(result)

    def test_serialize_message(self):
        self._add_member(self.member, self.member_role)

        message = MessageService.create_message(user=self.member, room=self.room, body="Test message")

        serialized = MessageService.serialize(message)

        self.assertEqual(serialized["body"], "Test message")
        self.assertEqual(serialized["user"], self.member.username)
        self.assertIn("id", serialized)
        self.assertIn("created_at", serialized)
