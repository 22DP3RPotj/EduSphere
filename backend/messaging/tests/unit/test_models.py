from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

import pytest

pytestmark = pytest.mark.unit

from backend.messaging.models import Message
from backend.room.models import Room

User = get_user_model()


class MessageModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            name="User",
            username="user",
            email="user@email.com",
        )
        self.room = Room.objects.create(
            host=self.user,
            name="Test Room",
            description="",
            visibility=Room.Visibility.PUBLIC,
        )

    def test_message_creation(self):
        message = Message.objects.create(
            user=self.user,
            room=self.room,
            body="Hello world!",
        )
        self.assertEqual(message.body, "Hello world!")
        self.assertFalse(message.is_edited)

    def test_message_str(self):
        message = Message.objects.create(
            user=self.user,
            room=self.room,
            body="A" * 100,
        )
        self.assertEqual(str(message), "A" * 50 + "...")

    def test_message_str_short(self):
        message = Message.objects.create(
            user=self.user,
            room=self.room,
            body="Short",
        )
        self.assertEqual(str(message), "Short")

    def test_message_parent_validation(self):
        other_room = Room.objects.create(
            host=self.user,
            name="Other Room",
            description="",
            visibility=Room.Visibility.PUBLIC,
        )
        parent_message = Message.objects.create(
            user=self.user,
            room=other_room,
            body="Parent",
        )
        child_message = Message(
            user=self.user,
            room=self.room,
            body="Child",
            parent=parent_message,
        )
        with self.assertRaises(ValidationError):
            child_message.full_clean()
