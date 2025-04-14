from django.contrib.auth import get_user_model
from graphql import ExecutionResult
from graphql_jwt.testcases import JSONWebTokenTestCase


class UsersTests(JSONWebTokenTestCase):

    def setUp(self):
        self._username = "test_user"
        self._email = "test.user@email.com"

    def test_get_user(self):
        self.user = get_user_model().objects.create(username=self._username, email=self._email)
        self.client.authenticate(self.user)
        
        query = """
            query GetCurrentUser {
                me {
                    id
                    username
                    email
                }
            }
        """

        result: ExecutionResult = self.client.execute(query)
        self.assertEqual(result.data, {
            'me': {
                'id': str(self.user.id),
                'username': self._username,
                'email': self._email
            }
        })
