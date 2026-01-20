import tempfile

from graphql import ExecutionResult
from graphql_jwt.testcases import JSONWebTokenTestCase

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings

import pytest

pytestmark = pytest.mark.unit

from backend.access.enums import PermissionCode
from backend.access.models import Participant, Permission, Role
from backend.messaging.models import Message
from backend.room.models import Room, Topic
from backend.core.tests.utils import create_test_image

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
            "password2": "securepassword123",
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
            "password2": "4asdfgh56",
        }
        result: ExecutionResult = self.client.execute(mutation, variables)

        self.assertIsNotNone(result.errors)

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
        avatar = SimpleUploadedFile(
            "avatar.jpg", create_test_image(), content_type="image/jpeg"
        )
        mutation = """
            mutation UpdateUser($avatar: Upload) {
                updateUser(avatar: $avatar) {
                    user { avatar }
                }
            }
        """
        result: ExecutionResult = self.client.execute(
            mutation, variables={"avatar": avatar}
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
        self.other_user = User.objects.create_user(
            name="OtherUser",
            username="otheruser",
            email="other@email.com",
        )
        self.topic = Topic.objects.create(name="ExistingTopic")

        Permission.objects.get_or_create(
            code=PermissionCode.ROOM_UPDATE, defaults={"description": "Update room"}
        )
        Permission.objects.get_or_create(
            code=PermissionCode.ROOM_DELETE, defaults={"description": "Delete room"}
        )

    def test_create_room_success(self):
        self.client.authenticate(self.user)
        mutation = """
            mutation CreateRoom($name: String!, $topicNames: [String!]!, $description: String!, $visibility: RoomVisibility!) {
                createRoom(name: $name, topicNames: $topicNames, description: $description, visibility: $visibility) {
                    room {
                        id
                        name
                        visibility
                        host { username }
                    }
                }
            }
        """
        variables = {
            "name": "New Room",
            "topicNames": ["NewTopic"],
            "description": "A test room",
            "visibility": "PUBLIC",
        }
        result: ExecutionResult = self.client.execute(mutation, variables)
        self.assertIsNone(result.errors)
        room = Room.objects.get(name="New Room")
        self.assertEqual(room.host, self.user)
        self.assertEqual(room.visibility, Room.Visibility.PUBLIC)
        self.assertIsNotNone(room.default_role)
        self.assertTrue(Participant.objects.filter(user=self.user, room=room).exists())

    def test_create_room_private(self):
        self.client.authenticate(self.user)
        mutation = """
            mutation CreateRoom($name: String!, $topicNames: [String!]!, $description: String!, $visibility: RoomVisibility!) {
                createRoom(name: $name, topicNames: $topicNames, description: $description, visibility: $visibility) {
                    room {
                        visibility
                    }
                }
            }
        """
        variables = {
            "name": "Private Room",
            "topicNames": [],
            "description": "",
            "visibility": "PRIVATE",
        }
        result: ExecutionResult = self.client.execute(mutation, variables)
        self.assertIsNone(result.errors)
        self.assertEqual(result.data["createRoom"]["room"]["visibility"], "PRIVATE")

    def test_update_room_success(self):
        room = Room.objects.create(
            host=self.user,
            name="Test Room",
            description="Old description",
            visibility=Room.Visibility.PUBLIC,
        )
        room.topics.add(self.topic)

        member_role = Role.objects.create(
            room=room, name="Member", description="", priority=0
        )
        owner_role = Role.objects.create(
            room=room, name="Owner", description="", priority=100
        )

        update_perm = Permission.objects.get(code=PermissionCode.ROOM_UPDATE)
        owner_role.permissions.add(update_perm)

        room.default_role = member_role
        room.save()
        Participant.objects.create(user=self.user, room=room, role=owner_role)

        self.client.authenticate(self.user)
        mutation = """
            mutation UpdateRoom($roomId: UUID!, $name: String, $description: String, $visibility: RoomVisibility) {
                updateRoom(roomId: $roomId, name: $name, description: $description, visibility: $visibility) {
                    room {
                        name
                        description
                        visibility
                    }
                }
            }
        """
        variables = {
            "roomId": str(room.id),
            "name": "Updated Room",
            "description": "New description",
            "visibility": "PRIVATE",
        }
        result: ExecutionResult = self.client.execute(mutation, variables)
        self.assertIsNone(result.errors)
        room.refresh_from_db()
        self.assertEqual(room.name, "Updated Room")
        self.assertEqual(room.description, "New description")
        self.assertEqual(room.visibility, Room.Visibility.PRIVATE)

    def test_delete_room_success(self):
        room = Room.objects.create(host=self.user, name="Test Room", description="")
        room.topics.add(self.topic)

        member_role = Role.objects.create(
            room=room, name="Member", description="", priority=0
        )
        owner_role = Role.objects.create(
            room=room, name="Owner", description="", priority=100
        )

        delete_perm = Permission.objects.get(code=PermissionCode.ROOM_DELETE)
        owner_role.permissions.add(delete_perm)

        room.default_role = member_role
        room.save()
        Participant.objects.create(user=self.user, room=room, role=owner_role)

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

    def test_delete_room_not_owner(self):
        room = Room.objects.create(host=self.user, name="Test Room", description="")
        role = Role.objects.create(room=room, name="Member", description="", priority=0)
        room.default_role = role
        room.save()
        Participant.objects.create(user=self.other_user, room=room, role=role)

        self.client.authenticate(self.other_user)
        mutation = """
            mutation DeleteRoom($roomId: UUID!) {
                deleteRoom(roomId: $roomId) {
                    success
                }
            }
        """
        variables = {"roomId": str(room.id)}
        result: ExecutionResult = self.client.execute(mutation, variables)
        self.assertIsNotNone(result.errors)

    def test_join_room_success(self):
        room = Room.objects.create(
            host=self.user,
            name="Test Room",
            description="",
            visibility=Room.Visibility.PUBLIC,
        )
        role = Role.objects.create(room=room, name="Member", description="", priority=0)
        room.default_role = role
        room.save()
        owner_role = Role.objects.create(
            room=room, name="Owner", description="", priority=100
        )
        Participant.objects.create(user=self.user, room=room, role=owner_role)

        self.client.authenticate(self.other_user)
        mutation = """
            mutation JoinRoom($roomId: UUID!) {
                joinRoom(roomId: $roomId) {
                    room { id }
                }
            }
        """
        variables = {"roomId": str(room.id)}
        result: ExecutionResult = self.client.execute(mutation, variables)
        self.assertIsNone(result.errors)
        self.assertTrue(
            Participant.objects.filter(user=self.other_user, room=room).exists()
        )

    def test_join_room_already_participant(self):
        room = Room.objects.create(
            host=self.user,
            name="Test Room",
            description="",
            visibility=Room.Visibility.PUBLIC,
        )
        role = Role.objects.create(room=room, name="Member", description="", priority=0)
        room.default_role = role
        room.save()
        Participant.objects.create(user=self.other_user, room=room, role=role)

        self.client.authenticate(self.other_user)
        mutation = """
            mutation JoinRoom($roomId: UUID!) {
                joinRoom(roomId: $roomId) {
                    room { id }
                }
            }
        """
        variables = {"roomId": str(room.id)}
        result: ExecutionResult = self.client.execute(mutation, variables)
        self.assertIsNotNone(result.errors)


class MessageMutationsTests(JSONWebTokenTestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            name="TestUser",
            username="testuser",
            email="test@email.com",
        )
        self.other_user = User.objects.create_user(
            name="OtherUser",
            username="otheruser",
            email="other@email.com",
        )
        self.room = Room.objects.create(
            host=User.objects.create_user(
                name="HostUser",
                username="hostuser",
                email="host@email.com",
            ),
            name="Test Room",
            description="",
        )
        self.topic = Topic.objects.create(name="TestTopic")
        self.room.topics.add(self.topic)
        self.role = Role.objects.create(
            room=self.room, name="Member", description="", priority=0
        )
        self.room.default_role = self.role
        self.room.save()
        Participant.objects.create(user=self.user, room=self.room, role=self.role)

    def test_delete_message_success(self):
        message = Message.objects.create(author=self.user, room=self.room, body="Test")
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
        message = Message.objects.create(
            author=self.user, room=self.room, body="Original"
        )
        self.client.authenticate(self.user)
        mutation = """
            mutation UpdateMessage($messageId: UUID!, $body: String!) {
                updateMessage(messageId: $messageId, body: $body) {
                    message { body isEdited }
                }
            }
        """
        variables = {"messageId": str(message.id), "body": "Updated"}
        result: ExecutionResult = self.client.execute(mutation, variables)
        self.assertIsNone(result.errors)
        message.refresh_from_db()
        self.assertEqual(message.body, "Updated")
        self.assertTrue(message.is_edited)

    def test_update_message_not_owner(self):
        message = Message.objects.create(
            author=self.user, room=self.room, body="Original"
        )
        self.client.authenticate(self.other_user)
        mutation = """
            mutation UpdateMessage($messageId: UUID!, $body: String!) {
                updateMessage(messageId: $messageId, body: $body) {
                    message { body }
                }
            }
        """
        variables = {"messageId": str(message.id), "body": "Updated"}
        result: ExecutionResult = self.client.execute(mutation, variables)
        self.assertIsNotNone(result.errors)


class UserAdminMutationsTests(JSONWebTokenTestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            name="AdminUser",
            username="adminuser",
            email="admin@email.com",
            is_staff=True,
            is_superuser=True,
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

    # TODO: rework
    # def test_update_user_active_status(self):
    #     self.client.authenticate(self.admin)
    #     mutation = """
    #         mutation UpdateUserActiveStatus($userIds: [UUID!]!, $isActive: Boolean!) {
    #             updateUserActiveStatus(userIds: $userIds, isActive: $isActive) {
    #                 success
    #                 updatedCount
    #             }
    #         }
    #     """
    #     variables = {
    #         "userIds": [str(self.user1.id), str(self.user2.id)],
    #         "isActive": False,
    #     }
    #     result: ExecutionResult = self.client.execute(mutation, variables)
    #     self.assertIsNone(result.errors)
    #     self.assertTrue(result.data["updateUserActiveStatus"]["success"])
    #     self.assertEqual(result.data["updateUserActiveStatus"]["updatedCount"], 2)

    #     self.user1.refresh_from_db()
    #     self.user2.refresh_from_db()
    #     self.assertFalse(self.user1.is_active)
    #     self.assertFalse(self.user2.is_active)

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
        variables = {"userIds": [str(self.user1.id)], "isStaff": True}
        result: ExecutionResult = self.client.execute(mutation, variables)
        self.assertIsNone(result.errors)
        self.assertTrue(result.data["updateUserStaffStatus"]["success"])
        self.assertEqual(result.data["updateUserStaffStatus"]["updatedCount"], 1)

        self.user1.refresh_from_db()
        self.assertTrue(self.user1.is_staff)
