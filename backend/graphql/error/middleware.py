import inspect
import logging
from typing import Any, Callable, NoReturn, Optional

import graphene
from graphql import GraphQLError
from graphql_jwt.exceptions import JSONWebTokenError

from backend.core.exceptions import ErrorCode, format_form_errors

logger = logging.getLogger(__name__)


class InternalErrorMiddleware:
    """
    Catches unhandled exceptions from resolvers and converts them to a
    safe INTERNAL_ERROR GraphQL error, preventing stack traces leaking to clients.
    """

    def resolve(
        self,
        next_: Callable,
        root: Any,
        info: graphene.ResolveInfo,
        **kwargs: Any,
    ) -> Any:
        try:
            result = next_(root, info, **kwargs)
        except (GraphQLError, JSONWebTokenError):
            raise
        except Exception:
            self._log_resolver_error(info)
            raise GraphQLError(
                "Internal error",
                extensions={"code": ErrorCode.INTERNAL_ERROR},
            )

        if inspect.isawaitable(result):

            async def handle():
                try:
                    return await result
                except (GraphQLError, JSONWebTokenError):
                    raise
                except Exception:
                    self._log_resolver_error(info)
                    raise GraphQLError(
                        "Internal error",
                        extensions={"code": ErrorCode.INTERNAL_ERROR},
                    )

            return handle()

        return result

    def _log_resolver_error(self, info: graphene.ResolveInfo):
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


class ErrorTransformingMiddleware:
    """
    Converts payload-style errors like:

        data: { register: { errors: {...} } }

    into proper GraphQL errors:

        errors: [...]
    """

    def resolve(
        self,
        next_: Callable,
        root: Any,
        info: graphene.ResolveInfo,
        **kwargs: Any,
    ) -> Any:
        result = next_(root, info, **kwargs)

        if inspect.isawaitable(result):

            async def handle():
                resolved = await result
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
        normalized = self._normalize_errors(raw_errors)
        raise GraphQLError(
            "Validation error",
            extensions={
                "code": ErrorCode.VALIDATION_ERROR,
                "errors": normalized or {"nonFieldErrors": [str(raw_errors)]},
            },
        )

    def _normalize_errors(self, errors: Any) -> Optional[dict]:
        if hasattr(errors, "get_json_data") and callable(errors.get_json_data):
            return format_form_errors(errors)

        if isinstance(errors, dict):
            normalized = {}
            for field, value in errors.items():
                messages = self._normalize_message_list(value)
                if messages:
                    normalized[str(field)] = messages
            return normalized or None

        if isinstance(errors, (list, tuple, set)):
            if all(
                hasattr(item, "field") and hasattr(item, "messages") for item in errors
            ):
                normalized = {}
                for item in errors:
                    field = str(getattr(item, "field", None) or "nonFieldErrors")
                    messages = self._normalize_message_list(
                        getattr(item, "messages", None)
                    )
                    if messages:
                        normalized[field] = self._dedupe(
                            normalized.get(field, []) + messages
                        )
                return normalized or None

            messages = self._normalize_message_list(errors)
            return {"nonFieldErrors": messages} if messages else None

        messages = self._normalize_message_list(errors)
        return {"nonFieldErrors": messages} if messages else None

    def _dedupe(self, items: list) -> list:
        return list(dict.fromkeys(items))

    def _normalize_message_list(self, value: Any) -> list:
        if value is None:
            return []
        if hasattr(value, "messages"):
            return self._dedupe([str(m) for m in value.messages])
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
