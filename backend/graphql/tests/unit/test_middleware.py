import pytest
import asyncio
from django.test import SimpleTestCase
from graphql import GraphQLError

from backend.core.exceptions import ErrorCode
from backend.graphql.error.middleware import ErrorTransformingMiddleware

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

    # TODO: Should be covered by InternalErrorMiddleware instead
    # def test_check_errors_raises_internal_error_on_unexpected_exception(self):
    #     class BadPayload:
    #         @property
    #         def errors(self):
    #             raise RuntimeError("boom")

    #     with self.assertRaises(GraphQLError) as ctx:
    #         self.middleware._check_errors(BadPayload())

    #     err = ctx.exception
    #     self.assertEqual(err.extensions["code"], ErrorCode.INTERNAL_ERROR)

    def test_check_errors_noop_when_errors_is_none(self):
        self.middleware._check_errors(_Payload(None))

    def test_check_errors_noop_with_empty_dict(self):
        self.middleware._check_errors({})

    def test_resolve_async_payload_error_raises_validation_error(self):
        async def next_(root, info, **kwargs):
            return _Payload(
                _ErrorDictLike(
                    {"email": [{"message": "User with this Email already exists."}]}
                )
            )

        class Info:
            field_name = "test"
            operation = None

        with self.assertRaises(GraphQLError) as ctx:
            asyncio.run(self.middleware.resolve(next_, None, Info()))

        err = ctx.exception
        self.assertEqual(err.extensions["code"], ErrorCode.VALIDATION_ERROR)
        self.assertEqual(
            err.extensions["errors"],
            {"email": ["User with this Email already exists."]},
        )
