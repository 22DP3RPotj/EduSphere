from graphql import ExecutionResult
from django.contrib.auth import get_user_model
from graphql_jwt.testcases import JSONWebTokenTestCase

from backend.core.models import Room, Topic, Message

User = get_user_model()

class QueryTests(JSONWebTokenTestCase):
    def setUp(self):
        
        self.user = User.objects.create_user(
            name="Test User",
            username="testuser",
            email="test@email.com",
        )
        
        self.topic_tech = Topic.objects.create(name="Tech")
        self.topic_music = Topic.objects.create(name="Music")
        
        self.room = Room.objects.create(
            host=self.user,
            name="Test Room",
            description="Test Description"
        )
        self.room.topics.add(self.topic_tech)
        
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
        self.room.participants.add(self.user)
        self.client.authenticate(self.user)
        
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
    
    def test_rooms_with_filters(self):
        query = """
            query GetRooms($search: String, $topics: [String!]) {
                rooms(search: $search, topics: $topics) {
                    name
                }
            }
        """
        variables = {"search": "Test"}
        result: ExecutionResult = self.client.execute(query, variables)
        self.assertEqual(len(result.data["rooms"]), 1)

        variables = {"topics": ["Tech"]}
        result: ExecutionResult = self.client.execute(query, variables)
        self.assertEqual(len(result.data["rooms"]), 1)

    def test_rooms_participated_by_user(self):
        self.client.authenticate(self.user)
        query = """
            query GetParticipatedRooms($userSlug: String!) {
                roomsParticipatedByUser(userSlug: $userSlug) {
                    name
                }
            }
        """
        self.room.participants.add(self.user)
        variables = {"userSlug": self.user.username}
        result: ExecutionResult = self.client.execute(query, variables)
        self.assertEqual(len(result.data["roomsParticipatedByUser"]), 1)

    def test_auth_status_unauthenticated(self):
        query = """
            query {
                authStatus {
                    isAuthenticated
                    user {
                        id
                    }
                }
            }
        """
        result: ExecutionResult = self.client.execute(query)
        self.assertFalse(result.data["authStatus"]["isAuthenticated"])
        self.assertIsNone(result.data["authStatus"]["user"])

    def test_topics_query(self):
        query = """
            query GetTopics {
                topics {
                    name
                }
            }
        """
        result: ExecutionResult = self.client.execute(query)
        self.assertEqual(len(result.data["topics"]), 2)
        topic_names = [topic["name"] for topic in result.data["topics"]]
        self.assertIn("Tech", topic_names)
        self.assertIn("Music", topic_names)

    def test_users_query_with_search(self):
        query = """
            query GetUsers($search: String) {
                users(search: $search) {
                    username
                }
            }
        """
        variables = {"search": "Test"}
        result: ExecutionResult = self.client.execute(query, variables)
        self.assertEqual(len(result.data["users"]), 1)
        self.assertEqual(result.data["users"][0]["username"], "testuser")