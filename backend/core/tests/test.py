from django.test import TestCase
from graphene.test import Client
from django.contrib.auth import get_user_model
from backend.core.models import Topic, Room, Message
from backend.core.schema import schema


User = get_user_model()

class GraphQLMutationsTests(TestCase):

    def setUp(self):
        self.client = Client(schema)
        self.user = User.objects.create_user(
            email="test@user.com",
            username="testuser",
            name="Test User",
            password="testpass123"
        )
        self.topic = Topic.objects.create(name="Testing")
        self.room = Room.objects.create(
            name="Test Room",
            host=self.user,
            topic=self.topic,
            description="Initial description"
        )
        self.message = Message.objects.create(
            user=self.user,
            room=self.room,
            body="Test message content"
        )
        
    def get_user_token(self):
        mutation = """
            mutation TokenAuth($email: String!, $password: String!) {
                tokenAuth(email: $email, password: $password) {
                    token
                }
            }
        """
        variables = {"email": "test@user.com", "password": "testpass123"}
        executed = self.client.execute(mutation, variables=variables)
        return executed["data"]["tokenAuth"]["token"]

    # def test_register_user(self):
    #     mutation = """
    #         mutation Register(
    #             $username: String!,
    #             $name: String!,
    #             $email: String!,
    #             $password1: String!,
    #             $password2: String!
    #         ) {
    #             registerUser(
    #                 username: $username,
    #                 name: $name,
    #                 email: $email,
    #                 password1: $password1,
    #                 password2: $password2
    #             ) {
    #                 user {
    #                     username
    #                     email
    #                 }
    #             }
    #         }
    #     """
    #     variables = {
    #         "username": "newuser",
    #         "name": "New User",
    #         "email": "new@user.com",
    #         "password1": "complexpass123",
    #         "password2": "complexpass123"
    #     }
    #     executed = self.client.execute(mutation, variables=variables)
    #     self.assertIsNone(executed.get("errors"))
    #     self.assertEqual(executed["data"]["registerUser"]["user"]["email"], "new@user.com")

    def test_create_room_authenticated(self):
        # token = self.get_user_token()
        mutation = """
            mutation CreateRoom($name: String!, $topic_id: ID!, $description: String) {
                createRoom(name: $name, topicId: $topic_id, description: $description) {
                    room {
                        name
                        description
                        host { username }
                    }
                }
            }
        """
        variables = {
            "name": "New Test Room",
            "topic_id": str(self.topic.id),
            "description": "Test description"
        }
        executed = self.client.execute(mutation, variables=variables, context={"user": self.user})
        # self.assertIsNone(executed.get("errors"))
        print(f'{executed=}')
        print(f'{type(executed)=}')
        self.assertEqual(executed["data"]["createRoom"]["room"]["name"], "New Test Room")

    # def test_create_room_unauthenticated(self):
    #     mutation = """
    #         mutation CreateRoom($name: String!, $topic_id: ID!) {
    #             createRoom(name: $name, topicId: $topic_id) {
    #                 room { id }
    #             }
    #         }
    #     """
    #     variables = {"name": "Unauthorized Room", "topic_id": str(self.topic.id)}
    #     executed = self.client.execute(mutation, variables=variables)
    #     self.assertIsNotNone(executed["errors"])
    #     self.assertEqual(executed["errors"][0]["message"], "Permission Denied")

    # def test_update_user(self):
    #     token = self.get_user_token()
    #     mutation = """
    #         mutation UpdateUser($name: String, $bio: String) {
    #             updateUser(name: $name, bio: $bio) {
    #                 user {
    #                     name
    #                     bio
    #                 }
    #             }
    #         }
    #     """
    #     variables = {"name": "Updated Name", "bio": "New bio content"}
    #     executed = self.client.execute(
    #         mutation,
    #         variables=variables,
    #         context_value={"user": self.user}
    #     )
    #     self.assertIsNone(executed.get("errors"))
    #     self.user.refresh_from_db()
    #     self.assertEqual(self.user.name, "Updated Name")

    # def test_delete_room_as_host(self):
    #     token = self.get_user_token()
    #     mutation = """
    #         mutation DeleteRoom($room_id: UUID!) {
    #             deleteRoom(roomId: $room_id) {
    #                 success
    #             }
    #         }
    #     """
    #     variables = {"room_id": str(self.room.id)}
    #     executed = self.client.execute(
    #         mutation,
    #         variables=variables,
    #         context_value={"user": self.user}
    #     )
    #     self.assertIsNone(executed.get("errors"))
    #     self.assertFalse(Room.objects.filter(id=self.room.id).exists())

    # def test_delete_room_as_non_host(self):
    #     other_user = User.objects.create_user(
    #         email="other@user.com",
    #         username="otheruser",
    #         password="testpass123"
    #     )
    #     mutation = """
    #         mutation DeleteRoom($room_id: UUID!) {
    #             deleteRoom(roomId: $room_id) {
    #                 success
    #             }
    #         }
    #     """
    #     variables = {"room_id": str(self.room.id)}
    #     executed = self.client.execute(
    #         mutation,
    #         variables=variables,
    #         context_value={"user": other_user}
    #     )
    #     self.assertIsNotNone(executed["errors"])
    #     self.assertTrue(Room.objects.filter(id=self.room.id).exists())

    # def test_delete_message_as_author(self):
    #     token = self.get_user_token()
    #     mutation = """
    #         mutation DeleteMessage($message_id: UUID!) {
    #             deleteMessage(messageId: $message_id) {
    #                 success
    #             }
    #         }
    #     """
    #     variables = {"message_id": str(self.message.id)}
    #     executed = self.client.execute(
    #         mutation,
    #         variables=variables,
    #         context_value={"user": self.user}
    #     )
    #     self.assertIsNone(executed.get("errors"))
    #     self.assertFalse(Message.objects.filter(id=self.message.id).exists())

    # def test_join_room(self):
    #     token = self.get_user_token()
    #     mutation = """
    #         mutation JoinRoom($room_id: UUID!) {
    #             joinRoom(roomId: $room_id) {
    #                 room {
    #                     participants { username }
    #                 }
    #             }
    #         }
    #     """
    #     variables = {"room_id": str(self.room.id)}
    #     executed = self.client.execute(
    #         mutation,
    #         variables=variables,
    #         context_value={"user": self.user}
    #     )
    #     self.assertIsNone(executed.get("errors"))
    #     self.assertIn(self.user.username, [p["username"] for p in executed["data"]["joinRoom"]["room"]["participants"]])

    # def test_create_topic(self):
    #     mutation = """
    #         mutation CreateTopic($name: String!) {
    #             createTopic(name: $name) {
    #                 topic {
    #                     name
    #                 }
    #             }
    #         }
    #     """
    #     variables = {"name": "New Topic"}
    #     executed = self.client.execute(mutation, variables=variables)
    #     self.assertIsNone(executed.get("errors"))
    #     self.assertTrue(Topic.objects.filter(name="New Topic").exists())
        
