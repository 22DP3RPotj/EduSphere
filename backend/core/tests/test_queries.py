from graphql import ExecutionResult
from django.contrib.auth import get_user_model
from graphql_jwt.testcases import JSONWebTokenTestCase


class QueryTests(JSONWebTokenTestCase):
    def setUp(self):
        from backend.core.models import Room, Topic, Message
        
        self.user = get_user_model().objects.create_user(
            name="Test User",
            username="testuser",
            email="test@email.com",
        )
        self.topic = Topic.objects.create(name="Tech")
        self.room = Room.objects.create(
            host=self.user,
            name="Test Room",
            topic=self.topic,
            description="Test Description"
        )
        self.message = Message.objects.create(
            user=self.user,
            room=self.room,
            body="Hello!"
        )

    def test_rooms_query(self):
        query = """
            query GetRooms {
                rooms {
                    name
                    description
                }
            }
        """
        result: ExecutionResult = self.client.execute(query)
        self.assertEqual(len(result.data["rooms"]), 1)
        self.assertEqual(result.data["rooms"][0]["name"], self.room.name)

    def test_me_query(self):
        self.client.authenticate(self.user)
        query = """
            query { 
                me {
                    username
                }
            }
        """
        result: ExecutionResult = self.client.execute(query)
        self.assertEqual(result.data["me"]["username"], "testuser")

    def test_auth_status_authenticated(self):
        self.client.authenticate(self.user)
        query = """
            query {
                authStatus {
                    isAuthenticated
                    user {
                        username
                    }
                }
            }
        """
        result: ExecutionResult = self.client.execute(query)
        self.assertTrue(result.data["authStatus"]["isAuthenticated"])
        self.assertEqual(result.data["authStatus"]["user"]["username"], self.user.username)

    def test_messages_query(self):
        query = """
            query GetMessages($hostSlug: String!, $roomSlug: String!) {
                messages(hostSlug: $hostSlug, roomSlug: $roomSlug) {
                    body
                }
            }
        """
        variables = {"hostSlug": self.user.username, "roomSlug": self.room.slug}
        result: ExecutionResult = self.client.execute(query, variables)
        self.assertEqual(result.data["messages"][0]["body"], self.message.body)
    