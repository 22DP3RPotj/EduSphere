import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

pytestmark = pytest.mark.unit

from backend.room.models import Room, Topic

User = get_user_model()


class TopicModelTest(TestCase):
    def test_topic_creation(self):
        topic = Topic.objects.create(name="Programming")
        assert topic.name == "Programming"

    def test_topic_str(self):
        topic = Topic.objects.create(name="Music")
        assert str(topic) == "Music"

    def test_topic_invalid_name(self):
        topic = Topic(name="\x01control")
        with pytest.raises(ValidationError):
            topic.full_clean()

    def test_topic_name_with_numbers(self):
        topic = Topic.objects.create(name="Music101")
        assert topic.name == "Music101"

    def test_topic_name_with_spaces(self):
        topic = Topic.objects.create(name="Data Science")
        assert topic.name == "Data Science"

    def test_topic_name_with_unicode(self):
        topic = Topic.objects.create(name="Программирование")
        assert topic.name == "Программирование"

    def test_topic_name_whitespace_only_invalid(self):
        topic = Topic(name="   ")
        with pytest.raises(ValidationError):
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
        assert room.name == "Test Room"
        assert room.host == self.user
        assert room.visibility == Room.Visibility.PUBLIC

    def test_room_unique_constraint(self):
        Room.objects.create(
            host=self.user,
            name="Duplicate Room",
            description="",
            visibility=Room.Visibility.PUBLIC,
        )
        with pytest.raises(ValidationError):
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
        assert str(room) == "Test Room"
