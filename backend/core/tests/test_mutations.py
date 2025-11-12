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
        user = User.objects.create_user(
            name="TestUser",
            username="testuser",
            email="test@email.com",
        )
        self.client.authenticate(user)
        mutation = """
            mutation UpdateUser($name: String) {
                updateUser(name: $name) {
                    user { name }
                }
            }
        """
        variables = {"name": "newusername"}
        result: ExecutionResult = self.client.execute(mutation, variables)
        user.refresh_from_db()
        self.assertEqual(user.name, "newusername")
        self.assertEqual(result.data["updateUser"]["user"]["name"], "newusername")

    def test_update_user_avatar(self):
        user = User.objects.create_user(
            name="TestUser",
            username="testuser",
            email="test@email.com",
        )
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
        self.user = User.objects.create_user(
            name="TestHost",
            username="testhost",
            email="host@email.com",
        )
        self.topic = Topic.objects.create(name="ExistingTopic")

    def test_create_room_success(self):
        self.client.authenticate(self.user)
        mutation = """
            mutation CreateRoom($name: String!, $topicNames: [String!]!, $description: String!) {
                createRoom(name: $name, topicNames: $topicNames, description: $description) {
                    room {
                        name
                        topics { name }
                        host { username }
                    }
                }
            }
        """
        variables = {"name": "New Room", "topicNames": ["NewTopic"], "description": ""}
        result: ExecutionResult = self.client.execute(mutation, variables)
        self.assertIsNone(result.errors)
        room = Room.objects.get(name="New Room")
        topic_names = list(room.topics.values_list("name", flat=True))
        self.assertIn("NewTopic", topic_names)
        self.assertEqual(room.host, self.user)

    def test_delete_room_success(self):
        room = Room.objects.create(host=self.user, name="Test Room", description="")
        room.topics.add(self.topic)

        self.client.authenticate(self.user)
        mutation = """
            mutation DeleteRoom($roomId: UUID!) {
                deleteRoom(roomId: $roomId) {
                    success
                }
            }
        """
        variables = {"roomId": str(room.id)}
        result: ExecutionResult = self.client.execute(mutation, variables)
        self.assertIsNone(result.errors)
        self.assertTrue(result.data["deleteRoom"]["success"])
        self.assertFalse(Room.objects.filter(id=room.id).exists())


class MessageMutationsTests(JSONWebTokenTestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            name="TestUser",
            username="testuser",
            email="test@email.com",
        )
        self.room = Room.objects.create(
            host=User.objects.create_user(
                name="HostUser",
                username="hostuser",
                email="host@email.com",
            ),
            name="Test Room",
            description=""
        )
        self.topic = Topic.objects.create(name="TestTopic")
        self.room.topics.add(self.topic)

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
        self.assertIsNone(result.errors)
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
        self.assertIsNone(result.errors)
        message.refresh_from_db()
        self.assertEqual(message.body, "Updated")

class UserAdminMutationsTests(JSONWebTokenTestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            name="AdminUser",
            username="adminuser",
            email="admin@email.com",
            is_staff=True,
            is_superuser=True
        )
        self.user1 = User.objects.create_user(
            name="User1",
            username="user1", 
            email="user1@email.com",
        )
        self.user2 = User.objects.create_user(
            name="User2",
            username="user2",
            email="user2@email.com", 
        )

    def test_update_user_active_status(self):
        self.client.authenticate(self.admin)
        mutation = """
            mutation UpdateUserActiveStatus($userIds: [UUID!]!, $isActive: Boolean!) {
                updateUserActiveStatus(userIds: $userIds, isActive: $isActive) {
                    success
                    updatedCount
                }
            }
        """
        variables = {
            "userIds": [str(self.user1.id), str(self.user2.id)],
            "isActive": False
        }
        result: ExecutionResult = self.client.execute(mutation, variables)
        self.assertIsNone(result.errors)
        self.assertTrue(result.data["updateUserActiveStatus"]["success"])
        self.assertEqual(result.data["updateUserActiveStatus"]["updatedCount"], 2)
        
        self.user1.refresh_from_db()
        self.user2.refresh_from_db()
        self.assertFalse(self.user1.is_active)
        self.assertFalse(self.user2.is_active)

    def test_update_user_staff_status(self):
        self.client.authenticate(self.admin)
        mutation = """
            mutation UpdateUserStaffStatus($userIds: [UUID!]!, $isStaff: Boolean!) {
                updateUserStaffStatus(userIds: $userIds, isStaff: $isStaff) {
                    success
                    updatedCount
                }
            }
        """
        variables = {
            "userIds": [str(self.user1.id)],
            "isStaff": True
        }
        result: ExecutionResult = self.client.execute(mutation, variables)
        self.assertIsNone(result.errors)
        self.assertTrue(result.data["updateUserStaffStatus"]["success"])
        self.assertEqual(result.data["updateUserStaffStatus"]["updatedCount"], 1)
        
        self.user1.refresh_from_db()
        self.assertTrue(self.user1.is_staff)
