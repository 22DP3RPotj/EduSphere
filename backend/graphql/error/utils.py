from functools import wraps
from typing import Callable, TypeVar, ParamSpec
from graphql_jwt.exceptions import JSONWebTokenError
from graphql import GraphQLError
from backend.core.exceptions import FormValidationException, DomainException

P = ParamSpec("P")
T = TypeVar("T")


def resolve_errors(f: Callable[P, T]) -> Callable[P, T]:
    @wraps(f)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        try:
            return f(*args, **kwargs)
        except (GraphQLError, JSONWebTokenError):
            raise  # Re-raise GraphQLError and JSONWebTokenError without modification
        except FormValidationException as e:
            raise GraphQLError(str(e), extensions={"code": e.code, "errors": e.errors})
        except DomainException as e:
            raise GraphQLError(str(e), extensions={"code": e.code})

    return wrapper
