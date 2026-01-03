import graphene

from backend.graphql.api import Query, Mutation


schema = graphene.Schema(
    query=Query,
    mutation=Mutation,
)
