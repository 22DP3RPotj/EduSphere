import graphene

from backend.graphql.api import Mutation, Query

schema = graphene.Schema(
    query=Query,
    mutation=Mutation,
)
