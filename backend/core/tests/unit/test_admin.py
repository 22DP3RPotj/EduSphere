from graphql import ExecutionResult
from django.contrib.auth import get_user_model
from graphql_jwt.testcases import JSONWebTokenTestCase

from backend.core.models import Room, Topic, Message

User = get_user_model()

class AdminQueryTests(JSONWebTokenTestCase):
    def setUp(self):
        
        self.user = User.objects.create_user(
            name="Test User",
            username="testuser",
            email="test@email.com",
            is_superuser=True
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

    def test_users_query_with_search(self):
        self.client.authenticate(self.user)
        
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

    def test_non_privileged_user_cannot_query_users(self):
        non_privileged_user = User.objects.create_user(
            name="Regular User",
            username="regularuser",
            email="regular@email.com",
            is_superuser=False
        )
        self.client.authenticate(non_privileged_user)
        
        query = """
            query GetUsers($search: String) {
                users(search: $search) {
                    username
                }
            }
        """
        variables = {"search": "Test"}
        result: ExecutionResult = self.client.execute(query, variables)
        self.assertIsNotNone(result.errors)
        self.assertTrue(len(result.errors) > 0)

