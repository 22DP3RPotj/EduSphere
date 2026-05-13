import pytest

from backend.core.exceptions import (
    FormValidationException,
    PermissionException,
    ValidationException,
)
from backend.core.tests.service_base import ServiceTestBase
from backend.messaging.models import Message, MessageStatus
from backend.messaging.services import MessageService, MessageStatusService

pytestmark = [pytest.mark.unit, pytest.mark.services]


class MessageServiceTest(ServiceTestBase):
    """Test MessageService methods."""

    def test_create_message_success(self):
        self._add_member(self.member, self.member_role)

        message = MessageService.create_message(
            user=self.member, room=self.room, body="Test message content"
        )

        assert message is not None
        assert message.author == self.member
        assert message.room == self.room
        assert message.body == "Test message content"
        assert not message.is_edited

    def test_create_message_not_participant(self):
        with pytest.raises(PermissionException):
            MessageService.create_message(
                user=self.other_user, room=self.room, body="Test message"
            )

    def test_create_message_invalid_data(self):
        self._add_member(self.member, self.member_role)

        with pytest.raises((ValidationException, FormValidationException)):
            MessageService.create_message(user=self.member, room=self.room, body="")

    def test_update_message_success(self):
        self._add_member(self.member, self.member_role)

        message = MessageService.create_message(
            user=self.member, room=self.room, body="Original content"
        )

        updated = MessageService.update_message(
            user=self.member, message=message, body="Updated content"
        )

        assert updated.body == "Updated content"
        assert updated.is_edited

    def test_update_message_not_author(self):
        self._add_member(self.member, self.member_role)
        self._add_member(self.other_user, self.member_role)

        message = MessageService.create_message(
            user=self.member, room=self.room, body="Test message"
        )

        with pytest.raises(PermissionException):
            MessageService.update_message(
                user=self.other_user, message=message, body="Hacked message"
            )

    def test_update_message_invalid_data(self):
        self._add_member(self.member, self.member_role)

        message = MessageService.create_message(
            user=self.member, room=self.room, body="Test message"
        )

        with pytest.raises(FormValidationException):
            MessageService.update_message(user=self.member, message=message, body="")

    def test_delete_message_author(self):
        self._add_member(self.member, self.member_role)

        message = MessageService.create_message(
            user=self.member, room=self.room, body="Test message"
        )

        result = MessageService.delete_message(self.member, message)

        assert result
        assert not Message.objects.filter(id=message.id).exists()

    def test_delete_message_not_author_no_permission(self):
        self._add_member(self.member, self.member_role)
        self._add_member(self.other_user, self.member_role)

        message = MessageService.create_message(
            user=self.member, room=self.room, body="Test message"
        )

        with pytest.raises(PermissionException):
            MessageService.delete_message(self.other_user, message)

    def test_delete_message_with_permission(self):
        self._add_member(self.member, self.member_role)

        message = MessageService.create_message(
            user=self.member, room=self.room, body="Test message"
        )

        result = MessageService.delete_message(self.owner, message)
        assert result

    def test_serialize_message(self):
        self._add_member(self.member, self.member_role)

        message = MessageService.create_message(
            user=self.member, room=self.room, body="Test message"
        )

        serialized = MessageService.serialize(message)

        assert serialized["body"] == "Test message"
        assert serialized["author"] == self.member.username
        assert "id" in serialized
        assert "created_at" in serialized


class MessageStatusServiceTest(ServiceTestBase):
    """Test MessageStatusService methods."""

    def setUp(self):
        super().setUp()
        self._add_member(self.member, self.member_role)
        self._add_member(self.other_user, self.member_role)
        self.message = MessageService.create_message(
            user=self.member, room=self.room, body="Test message"
        )

    def test_mark_delivered_creates_status_for_recipient(self):
        MessageStatusService.mark_delivered(
            user=self.other_user, message_ids=[self.message.id]
        )
        assert MessageStatus.objects.filter(
            message=self.message,
            user=self.other_user,
            status=MessageStatus.Status.DELIVERED,
        ).exists()

    def test_mark_delivered_excludes_author(self):
        MessageStatusService.mark_delivered(
            user=self.member, message_ids=[self.message.id]
        )
        assert not MessageStatus.objects.filter(
            message=self.message, user=self.member
        ).exists()

    def test_mark_delivered_is_idempotent(self):
        MessageStatusService.mark_delivered(
            user=self.other_user, message_ids=[self.message.id]
        )
        MessageStatusService.mark_delivered(
            user=self.other_user, message_ids=[self.message.id]
        )
        assert (
            MessageStatus.objects.filter(
                message=self.message, user=self.other_user
            ).count()
            == 1
        )

    def test_mark_seen_creates_seen_status(self):
        MessageStatusService.mark_seen(
            user=self.other_user, message_ids=[self.message.id]
        )
        assert MessageStatus.objects.filter(
            message=self.message,
            user=self.other_user,
            status=MessageStatus.Status.SEEN,
        ).exists()

    def test_mark_seen_upgrades_delivered_to_seen(self):
        MessageStatusService.mark_delivered(
            user=self.other_user, message_ids=[self.message.id]
        )
        MessageStatusService.mark_seen(
            user=self.other_user, message_ids=[self.message.id]
        )
        assert MessageStatus.objects.filter(
            message=self.message,
            user=self.other_user,
            status=MessageStatus.Status.SEEN,
        ).exists()
        assert not MessageStatus.objects.filter(
            message=self.message,
            user=self.other_user,
            status=MessageStatus.Status.DELIVERED,
        ).exists()

    def test_mark_seen_excludes_author(self):
        updates = MessageStatusService.mark_seen(
            user=self.member, message_ids=[self.message.id]
        )
        assert updates == []
        assert not MessageStatus.objects.filter(
            message=self.message, user=self.member
        ).exists()

    def test_mark_seen_no_duplicate_updates_when_already_seen(self):
        MessageStatusService.mark_seen(
            user=self.other_user, message_ids=[self.message.id]
        )
        updates = MessageStatusService.mark_seen(
            user=self.other_user, message_ids=[self.message.id]
        )
        assert updates == []
