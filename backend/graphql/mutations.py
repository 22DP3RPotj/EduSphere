import graphene
from typing import Any, Optional, Self
from backend.graphql.error.utils import resolve_errors


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
