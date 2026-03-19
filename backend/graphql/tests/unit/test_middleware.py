from django.test import SimpleTestCase
import pytest
from graphql import GraphQLError

from backend.core.exceptions import ErrorCode
from backend.graphql.middleware import ErrorTransformingMiddleware

pytestmark = pytest.mark.unit


class _Payload:
    def __init__(self, errors):
        self.errors = errors


class _ErrorDictLike:
    def __init__(self, data):
        self._data = data

    def get_json_data(self):
        return self._data


class _AuthErrorType:
    def __init__(self, field, messages):
        self.field = field
        self.messages = messages


class ErrorTransformingMiddlewareTests(SimpleTestCase):
    def setUp(self):
        self.middleware = ErrorTransformingMiddleware()

    def test_converts_error_dict_like_to_structured_extensions(self):
        payload = _Payload(
            _ErrorDictLike(
                {
                    "username": [
                        {"message": "User with this Username already exists."}
                    ],
                    "email": [{"message": "User with this Email already exists."}],
                }
            )
        )

        with self.assertRaises(GraphQLError) as ctx:
            self.middleware._check_errors(payload)

        err = ctx.exception
        self.assertEqual(err.extensions["code"], ErrorCode.VALIDATION_ERROR)
        self.assertEqual(
            err.extensions["errors"],
            {
                "username": ["User with this Username already exists."],
                "email": ["User with this Email already exists."],
            },
        )

    def test_converts_auth_error_list_to_field_map(self):
        payload = _Payload(
            [
                _AuthErrorType("username", ["User with this Username already exists."]),
                _AuthErrorType("email", ["User with this Email already exists."]),
            ]
        )

        with self.assertRaises(GraphQLError) as ctx:
            self.middleware._check_errors(payload)

        err = ctx.exception
        self.assertEqual(err.extensions["code"], ErrorCode.VALIDATION_ERROR)
        self.assertEqual(
            err.extensions["errors"],
            {
                "username": ["User with this Username already exists."],
                "email": ["User with this Email already exists."],
            },
        )

    def test_falls_back_to_non_field_error_for_string(self):
        with self.assertRaises(GraphQLError) as ctx:
            self.middleware._check_errors({"errors": "Invalid credentials"})

        err = ctx.exception
        self.assertEqual(err.extensions["code"], ErrorCode.VALIDATION_ERROR)
        self.assertEqual(
            err.extensions["errors"],
            {"nonFieldErrors": ["Invalid credentials"]},
        )
