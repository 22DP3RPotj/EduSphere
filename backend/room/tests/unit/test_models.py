from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

import pytest

pytestmark = pytest.mark.unit

from backend.room.models import Room, Topic

User = get_user_model()


class TopicModelTest(TestCase):
    def test_topic_creation(self):
        topic = Topic.objects.create(name="Programming")
        self.assertEqual(topic.name, "Programming")

    def test_topic_str(self):
        topic = Topic.objects.create(name="Music")
        self.assertEqual(str(topic), "Music")

    def test_topic_invalid_name(self):
        with self.assertRaises(ValidationError):
            topic = Topic(name="\x01control")
            topic.full_clean()

    def test_topic_name_with_numbers(self):
        topic = Topic.objects.create(name="Music101")
        self.assertEqual(topic.name, "Music101")

    def test_topic_name_with_spaces(self):
        topic = Topic.objects.create(name="Data Science")
        self.assertEqual(topic.name, "Data Science")

    def test_topic_name_with_unicode(self):
        topic = Topic.objects.create(name="Программирование")
        self.assertEqual(topic.name, "Программирование")

    def test_topic_name_whitespace_only_invalid(self):
        with self.assertRaises(ValidationError):
            topic = Topic(name="   ")
            topic.full_clean()


class RoomModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            name="Host",
            username="host",
            email="host@email.com",
        )

    def test_room_creation(self):
        room = Room.objects.create(
            host=self.user,
            name="Test Room",
            description="Test Description",
            visibility=Room.Visibility.PUBLIC,
        )
        self.assertEqual(room.name, "Test Room")
        self.assertEqual(room.host, self.user)
        self.assertEqual(room.visibility, Room.Visibility.PUBLIC)

    def test_room_unique_constraint(self):
        Room.objects.create(
            host=self.user,
            name="Duplicate Room",
            description="",
            visibility=Room.Visibility.PUBLIC,
        )
        with self.assertRaises(Exception):
            Room.objects.create(
                host=self.user,
                name="Duplicate Room",
                description="",
                visibility=Room.Visibility.PUBLIC,
            )

    def test_room_str(self):
        room = Room.objects.create(
            host=self.user,
            name="Test Room",
            description="",
            visibility=Room.Visibility.PUBLIC,
        )
        self.assertEqual(str(room), "Test Room")
