import inspect
from collections.abc import Callable
from functools import wraps

from graphql import GraphQLError
from graphql_jwt.exceptions import JSONWebTokenError

from backend.core.exceptions import DomainException, FormValidationException


def resolve_errors[**P, T](f: Callable[P, T]) -> Callable[P, T]:
    @wraps(f)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        try:
            result = f(*args, **kwargs)
        except (GraphQLError, JSONWebTokenError):
            raise
        except FormValidationException as e:
            raise GraphQLError(
                str(e), extensions={"code": e.code, "errors": e.errors}
            ) from e
        except DomainException as e:
            raise GraphQLError(str(e), extensions={"code": e.code}) from e

        if inspect.isawaitable(result):

            async def handle():
                try:
                    return await result
                except (GraphQLError, JSONWebTokenError):
                    raise
                except FormValidationException as e:
                    raise GraphQLError(
                        str(e), extensions={"code": e.code, "errors": e.errors}
                    ) from e
                except DomainException as e:
                    raise GraphQLError(str(e), extensions={"code": e.code}) from e

            return handle()

        return result

    return wrapper
