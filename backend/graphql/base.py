import logging
import graphene
from functools import wraps
from typing import Any, Callable, Optional, Self, TypeVar, ParamSpec
from graphql_jwt.exceptions import JSONWebTokenError
from graphql import GraphQLError
from backend.core.exceptions import FormValidationException, DomainException

logger = logging.getLogger(__name__)

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


class BaseMutation(graphene.Mutation):
    """Base class for all mutations, providing common functionality such as error handling."""

    class Meta:
        abstract = True

    @classmethod
    @resolve_errors
    def mutate(cls, root: Optional[Any], info: graphene.ResolveInfo, **kwargs) -> Self:
        return cls.resolve(root, info, **kwargs)

    @classmethod
    def resolve(cls, root: Optional[Any], info: graphene.ResolveInfo, **kwargs) -> Self:
        raise NotImplementedError(f"{cls.__name__}.resolve() must be implemented.")
