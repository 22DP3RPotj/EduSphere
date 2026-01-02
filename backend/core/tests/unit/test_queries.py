from graphql import ExecutionResult
from graphql_jwt.testcases import JSONWebTokenTestCase

from django.contrib.auth import get_user_model
from django.test import tag

from backend.messaging.models import Message
from backend.room.models import Room, Topic
from backend.access.models import Participant, Role

User = get_user_model()


@tag("unit")
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
            description="Test Description",
            visibility=Room.Visibility.PUBLIC
        )
        self.role = Role.objects.create(room=self.room, name="Member", description="", priority=0)
        self.room.default_role = self.role
        self.room.save()
        self.room.topics.add(self.topic_tech)
        
        Participant.objects.create(user=self.user, room=self.room, role=self.role)
        
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
                    visibility
                }
            }
        """
        result: ExecutionResult = self.client.execute(query)
        self.assertIsNone(result.errors, f"Unexpected errors: {result.errors}")
        self.assertIsNotNone(result.data)
        self.assertEqual(len(result.data["rooms"]), 1)
        self.assertEqual(result.data["rooms"][0]["name"], self.room.name)
        self.assertEqual(result.data["rooms"][0]["visibility"], "PUBLIC")

    def test_room_query(self):
        query = """
            query GetRoom($hostSlug: String!, $roomSlug: String!) {
                room(hostSlug: $hostSlug, roomSlug: $roomSlug) {
                    name
                    description
                    visibility
                }
            }
        """
        variables = {"hostSlug": self.user.username, "roomSlug": self.room.slug}
        result: ExecutionResult = self.client.execute(query, variables)
        self.assertIsNone(result.errors)
        self.assertEqual(result.data["room"]["name"], self.room.name)

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

    def test_auth_status_not_authenticated(self):
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
        self.assertFalse(result.data["authStatus"]["isAuthenticated"])
        self.assertIsNone(result.data["authStatus"]["user"])

    def test_messages_query(self):
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
        self.assertEqual(len(result.data["messages"]), 1)
        self.assertEqual(result.data["messages"][0]["body"], self.message.body)
    
    def test_rooms_with_search_filter(self):
        query = """
            query GetRooms($search: String) {
                rooms(search: $search) {
                    name
                }
            }
        """
        variables = {"search": "Test"}
        result: ExecutionResult = self.client.execute(query, variables)
        self.assertIsNone(result.errors, f"Unexpected errors: {result.errors}")
        self.assertIsNotNone(result.data)
        self.assertEqual(len(result.data["rooms"]), 1)

    def test_rooms_with_topic_filter(self):
        query = """
            query GetRooms($topics: [String!]) {
                rooms(topics: $topics) {
                    name
                }
            }
        """
        variables = {"topics": ["Tech"]}
        result: ExecutionResult = self.client.execute(query, variables)
        self.assertIsNone(result.errors, f"Unexpected errors: {result.errors}")
        self.assertIsNotNone(result.data)
        self.assertEqual(len(result.data["rooms"]), 1)

    def test_topics_query(self):
        query = """
            query GetTopics {
                topics {
                    name
                }
            }
        """
        result: ExecutionResult = self.client.execute(query)
        topic_names = [topic["name"] for topic in result.data["topics"]]
        self.assertIn("Tech", topic_names)
        self.assertIn("Music", topic_names)

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
        variables = {"userSlug": self.user.username}
        result: ExecutionResult = self.client.execute(query, variables)
        self.assertIsNone(result.errors, f"Unexpected errors: {result.errors}")
        self.assertIsNotNone(result.data)
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

