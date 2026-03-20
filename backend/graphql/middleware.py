import inspect
import logging
from typing import Any, NoReturn, Optional
from graphql import GraphQLError

from backend.core.exceptions import ErrorCode

logger = logging.getLogger(__name__)


class ErrorTransformingMiddleware:
    """
    Converts payload-style errors like:

    data: {
        register: {
            errors: {...}
        }
    }

    into proper GraphQL errors:

    errors: [...]
    """

    def resolve(self, next_, root, info, **kwargs):
        try:
            result = next_(root, info, **kwargs)
        except GraphQLError:
            raise
        except Exception as e:
            logger.error(
                "Unexpected error in GraphQL resolver",
                extra={
                    "field": info.field_name,
                    "operation": info.operation.name.value
                    if info.operation and info.operation.name
                    else None,
                },
                exc_info=True,
            )
            raise GraphQLError(
                "Internal error",
                extensions={"code": ErrorCode.INTERNAL_ERROR},
            ) from e

        # Handle async resolvers if present
        if inspect.isawaitable(result):

            async def handle():
                try:
                    resolved = await result
                except GraphQLError:
                    raise
                except Exception as e:
                    logger.error(
                        "Unexpected error in GraphQL resolver",
                        extra={
                            "field": info.field_name,
                            "operation": info.operation.name.value
                            if info.operation and info.operation.name
                            else None,
                        },
                        exc_info=True,
                    )
                    raise GraphQLError(
                        "Internal error",
                        extensions={"code": ErrorCode.INTERNAL_ERROR},
                    ) from e

                self._check_errors(resolved)
                return resolved

            return handle()

        self._check_errors(result)
        return result

    def _check_errors(self, result):
        if result is None:
            return

        errors = getattr(result, "errors", None)

        if not errors and isinstance(result, dict):
            errors = result.get("errors")

        if errors:
            self._raise_validation_error(errors)

    def _raise_validation_error(self, raw_errors: Any) -> NoReturn:
        normalized_errors = self._normalize_errors(raw_errors)
        if normalized_errors:
            raise GraphQLError(
                "Validation error",
                extensions={
                    "code": ErrorCode.VALIDATION_ERROR,
                    "errors": normalized_errors,
                },
            )

        raise GraphQLError(
            "Validation error",
            extensions={
                "code": ErrorCode.VALIDATION_ERROR,
                "errors": {"nonFieldErrors": [str(raw_errors)]},
            },
        )

    def _normalize_errors(self, errors: Any) -> Optional[dict]:
        # Django ErrorDict has get_json_data(), which gives a stable machine-readable format.
        if hasattr(errors, "get_json_data") and callable(errors.get_json_data):
            data = errors.get_json_data()
            if isinstance(data, dict):
                return {
                    field: self._dedupe(
                        [entry.get("message", str(entry)) for entry in entries]
                    )
                    for field, entries in data.items()
                }

        if isinstance(errors, dict):
            normalized = {}
            for field, value in errors.items():
                messages = self._normalize_message_list(value)
                if messages:
                    normalized[str(field)] = messages
            return normalized or None

        if isinstance(errors, (list, tuple, set)):
            # django-graphene-auth may return ErrorType-like objects with field/messages attrs.
            if all(
                hasattr(item, "field") and hasattr(item, "messages") for item in errors
            ):
                normalized = {}
                for item in errors:
                    field = getattr(item, "field", None) or "nonFieldErrors"
                    messages = self._normalize_message_list(
                        getattr(item, "messages", None)
                    )
                    if not messages:
                        continue
                    if str(field) not in normalized:
                        normalized[str(field)] = []
                    normalized[str(field)] = self._dedupe(
                        normalized.get(str(field), []) + messages
                    )
                return normalized or None

            messages = self._normalize_message_list(errors)
            if messages:
                return {"nonFieldErrors": messages}
            return None

        messages = self._normalize_message_list(errors)
        if messages:
            return {"nonFieldErrors": messages}
        return None

    def _dedupe(self, items: list) -> list:
        return list(dict.fromkeys(items))

    def _normalize_message_list(self, value: Any) -> list:
        if value is None:
            return []

        if hasattr(value, "messages"):
            return self._dedupe([str(message) for message in value.messages])

        if isinstance(value, str):
            return [value]

        if isinstance(value, dict):
            if "message" in value:
                return [str(value["message"])]
            if "messages" in value:
                return self._normalize_message_list(value["messages"])
            return [str(value)]

        if isinstance(value, (list, tuple, set)):
            messages = []
            for item in value:
                if isinstance(item, dict) and "message" in item:
                    item = item["message"]
                elif hasattr(item, "message"):
                    item = item.message

                messages.append(str(item))

            return self._dedupe(messages)

        return [str(value)]
