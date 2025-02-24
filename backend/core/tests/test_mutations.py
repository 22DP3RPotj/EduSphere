from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from graphql_jwt.shortcuts import get_token
import json

User = get_user_model()

class GraphQLTestCases(TestCase):
    def setUp(self):
        """Setup test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            name="Test User",
            email="test@example.com",
            password="securepassword"
        )
        self.token = get_token(self.user)

    def graphql_query(self, query, variables=None, headers=None):
        """Helper function to execute GraphQL queries"""
        body = {"query": query, "variables": variables or {}}
        response = self.client.post(
            "/graphql/",
            data=json.dumps(body),
            content_type="application/json",
            **(headers or {})
        )
        return response.json()

    def test_register_user(self):
        """Test user registration mutation"""
        mutation = """
        mutation RegisterUser {
            registerUser(username: "newuser", name: "New User", email: "new@example.com", password1: "1qwerty23", password2: "1qwerty23") {
                user {
                    id
                    username
                    email
                }
                token
            }
        }
        """
        response = self.graphql_query(mutation)
        self.assertIsNone(response.get("errors"))
        self.assertIn("registerUser", response.get("data"))

    def test_create_room(self):
        """Test creating a room"""
        mutation = """
        mutation CreateRoom {
            createRoom(name: "GraphQL Room", topicName: "Django", description: "Testing GraphQL") {
                room {
                    id
                    name
                    description
                }
            }
        }
        """
        headers = {"HTTP_AUTHORIZATION": f"JWT {self.token}"}
        response = self.graphql_query(mutation, headers=headers)
        self.assertIsNone(response.get("errors"))
        self.assertEqual(response["data"]["createRoom"]["room"]["name"], "GraphQL Room")

    def test_protected_mutation(self):
        """Test that protected mutations require authentication"""
        mutation = """
        mutation {
            deleteRoom(hostSlug: "testuser", roomSlug: "test-room") {
                success
            }
        }
        """
        response = self.graphql_query(mutation)
        self.assertIsNotNone(response.get("errors"))
