import tempfile
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from graphql import ExecutionResult
from graphql_jwt.testcases import JSONWebTokenTestCase

from backend.core.models import Room, Topic, Message
from .utils import create_test_image

User = get_user_model()

class UserMutationsTests(JSONWebTokenTestCase):
    def setUp(self):
        self.temp_media = tempfile.TemporaryDirectory()
        self.media_override = override_settings(MEDIA_ROOT=self.temp_media.name)
        self.media_override.enable()
    
    def tearDown(self):
        self.media_override.disable()
        self.temp_media.cleanup()
    
    def test_register_user_success(self):
        mutation = """
            mutation RegisterUser(
                $username: String!
                $name: String!
                $email: String!
                $password1: String!
                $password2: String!
            ) {
                registerUser(
                    email: $email
                    name: $name
                    password1: $password1
                    password2: $password2
                    username: $username
                ) {
                    user {
                        username
                        email
                    }
                    success
                }
            }
        """
        variables = {
            "username": "newuser",
            "name": "New User",
            "email": "new@email.com",
            "password1": "securepassword123",
            "password2": "securepassword123"
        }
        result: ExecutionResult = self.client.execute(mutation, variables)
        self.assertIsNone(result.errors)
        self.assertTrue(result.data["registerUser"]["success"])
        self.assertEqual(result.data["registerUser"]["user"]["username"], "newuser")
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_register_user_password_mismatch(self):
        mutation = """
            mutation RegisterUser(
                $username: String!
                $name: String!
                $email: String!
                $password1: String!
                $password2: String!
            ) {
                registerUser(
                    email: $email
                    name: $name
                    password1: $password1
                    password2: $password2
                    username: $username
                ) {
                    success
                }
            }
        """
        variables = {
            "username": "testuser",
            "name": "Test User",
            "email": "test@email.com",
            "password1": "1qwerty23",
            "password2": "4asdfgh56"
        }
        result: ExecutionResult = self.client.execute(mutation, variables)
        
        self.assertIsNotNone(result.errors)
        self.assertIn("password2", result.errors[0].extensions["errors"])

    def test_update_user_success(self):
        user = User.objects.create(name="TestUser", username="testuser", email="test@email.com")
        self.client.authenticate(user)
        mutation = """
            mutation UpdateUser($username: String) {
                updateUser(username: $username) {
                    user { username }
                }
            }
        """
        variables = {"username": "newusername"}
        result: ExecutionResult = self.client.execute(mutation, variables)
        user.refresh_from_db()
        self.assertEqual(user.username, "newusername")
        self.assertEqual(result.data["updateUser"]["user"]["username"], "newusername")

    def test_update_user_avatar(self):
        user = User.objects.create(name="TestUser", username="testuser", email="test@email.com")
        self.client.authenticate(user)
        avatar = SimpleUploadedFile("avatar.jpg", create_test_image(), content_type="image/jpeg")
        mutation = """
            mutation UpdateUser($avatar: Upload) {
                updateUser(avatar: $avatar) {
                    user { avatar }
                }
            }
        """
        result: ExecutionResult = self.client.execute(
            mutation,
            variables={"avatar": avatar}
        )
        self.assertIsNone(result.errors)
        user.refresh_from_db()
        self.assertTrue(user.avatar.name.endswith(".jpg"))

class RoomMutationsTests(JSONWebTokenTestCase):

    def setUp(self):
        self.user = User.objects.create(name="TestHost", username="testhost", email="host@email.com")
        self.topic = Topic.objects.create(name="Existing Topic")

    def test_create_room_success(self):
        self.client.authenticate(self.user)
        mutation = """
            mutation CreateRoom($name: String!, $topicName: String!) {
                createRoom(name: $name, topicName: $topicName) {
                    room {
                        name
                        topic { name }
                        host { username }
                    }
                }
            }
        """
        variables = {"name": "New Room", "topicName": "New Topic"}
        result: ExecutionResult = self.client.execute(mutation, variables)
        room = Room.objects.get(name="New Room")
        self.assertEqual(room.topic.name, "New Topic")
        self.assertEqual(room.host, self.user)

    def test_delete_room_success(self):
        room = Room.objects.create(host=self.user, name="Test Room", topic=self.topic)
        self.client.authenticate(self.user)
        mutation = """
            mutation DeleteRoom($hostSlug: String!, $roomSlug: String!) {
                deleteRoom(hostSlug: $hostSlug, roomSlug: $roomSlug) {
                    success
                }
            }
        """
        variables = {"hostSlug": self.user.slug, "roomSlug": room.slug}
        result: ExecutionResult = self.client.execute(mutation, variables)
        self.assertTrue(result.data["deleteRoom"]["success"])
        self.assertFalse(Room.objects.filter(id=room.id).exists())

class MessageMutationsTests(JSONWebTokenTestCase):

    def setUp(self):
        self.user = User.objects.create(name="TestUser", username="testuser", email="test@email.com")
        self.room = Room.objects.create(
            host=User.objects.create(username="hostuser"),
            name="Test Room",
            topic=Topic.objects.create(name="Test Topic")
        )

    def test_delete_message_success(self):
        message = Message.objects.create(user=self.user, room=self.room, body="Test")
        self.client.authenticate(self.user)
        mutation = """
            mutation DeleteMessage($messageId: UUID!) {
                deleteMessage(messageId: $messageId) { success }
            }
        """
        variables = {"messageId": str(message.id)}
        result: ExecutionResult = self.client.execute(mutation, variables)
        self.assertTrue(result.data["deleteMessage"]["success"])
        self.assertFalse(Message.objects.filter(id=message.id).exists())

    def test_update_message_success(self):
        message = Message.objects.create(user=self.user, room=self.room, body="Original")
        self.client.authenticate(self.user)
        mutation = """
            mutation UpdateMessage($messageId: UUID!, $body: String!) {
                updateMessage(messageId: $messageId, body: $body) {
                    message { body }
                }
            }
        """
        variables = {"messageId": str(message.id), "body": "Updated"}
        result: ExecutionResult = self.client.execute(mutation, variables)
        message.refresh_from_db()
        self.assertEqual(message.body, "Updated")