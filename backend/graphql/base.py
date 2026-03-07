import logging
from functools import wraps
from typing import Callable, Self, TypeVar, ParamSpec
from graphene import Mutation
from graphql import GraphQLError
from backend.core.exceptions import ErrorCode, FormValidationException, DomainException


logger = logging.getLogger(__name__)

P = ParamSpec("P")
T = TypeVar("T")


def resolve_errors(f: Callable[P, T]) -> Callable[P, T]:
    @wraps(f)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        try:
            return f(*args, **kwargs)
        except FormValidationException as e:
            raise GraphQLError(str(e), extensions={"code": e.code, "errors": e.errors})
        except DomainException as e:
            raise GraphQLError(str(e), extensions={"code": e.code})
        except Exception as e:
            logger.error("Unexpected error in mutation", exc_info=True)
            raise GraphQLError(
                "An unexpected error occurred.",
                extensions={"code": ErrorCode.INTERNAL_ERROR},
            ) from e

    return wrapper


class BaseMutation(Mutation):
    """Base class for all mutations, providing common functionality such as error handling."""

    class Meta:
        abstract = True

    @classmethod
    @resolve_errors
    def mutate(cls, root, info, **kwargs) -> Self:
        return cls.resolve(root, info, **kwargs)

    @classmethod
    def resolve(cls, root, info, **kwargs) -> Self:
        raise NotImplementedError(f"{cls.__name__}.resolve() must be implemented.")
